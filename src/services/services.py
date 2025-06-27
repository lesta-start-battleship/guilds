import hashlib
import os
import uuid

from fastapi import HTTPException
from repositories.processed_file import ProcessedFileRepository
from repositories.word_stat import WordStatRepository
from schemas.schemas import ProcessedResultResponse, TermResponse, MetricsResponse
from tasks import process_file_task

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def uploads_file(file, user_id: int):
    # fixme обработать ошибку с загрузкой такого же файла что уже был ранее загружен
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Сохраняем файл
    hash_md5 = hashlib.md5()
    with open(file_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):
            buffer.write(content)
            hash_md5.update(content)

    file_hash = hash_md5.hexdigest()
    task = process_file_task.delay(
        file_path,
        file_id,
        file_hash,
        owner_id=user_id,
        filename=file.filename
    )

    return {
        "file_id": file_id,
        "task_id": task.id,
        "status": "processing"
    }


async def task_status(task):
    """
    Функция проверки статуса задачи
    :param task:
    :return:
    """
    if task.state == 'PENDING':
        return {"status": "processing"}
    elif task.state == 'SUCCESS':
        result = task.result
        return {"status": "completed", "result": result}
    elif task.state == 'FAILURE':
        return {"status": "failed", "error": str(task.info)}
    else:
        return {"status": task.state}


async def get_result_def(db, file_id: str, page: int = 1, page_size: int = 50):
    """
    Получение результата обработки файла и статистики слов.
    """
    file_repo = ProcessedFileRepository(db)
    word_repo = WordStatRepository(db)

    processed_file = file_repo.get_by_file_id(file_id)
    if not processed_file:
        raise HTTPException(status_code=404, detail="File not found")

    total_terms = word_repo.count_by_file_id(file_id)
    total_pages = (total_terms + page_size - 1) // page_size

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="Page out of range")

    word_stats = word_repo.get_by_file_id_paginated(
        file_id=file_id,
        offset=(page - 1) * page_size,
        limit=page_size
    )

    if not word_stats:
        raise HTTPException(status_code=404, detail="WordStats not found")

    terms = [TermResponse(word=w.term, tf=w.tf, idf=w.idf) for w in word_stats]

    return ProcessedResultResponse(
        status=processed_file.status,
        result=processed_file.result,
        error=processed_file.error,
        created_at=processed_file.created_at,
        terms=terms,
        total_terms=total_terms,
        page=page,
        total_pages=total_pages
    )


async def delete_file_by_id(db, file_id: str):
    """
    Удаление файла и его данных.
    """
    file_repo = ProcessedFileRepository(db)
    file = file_repo.get_by_file_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.file_id}")
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(file)
    db.commit()

    return {"status": "success", "message": "File deleted successfully"}


async def get_custom_metrics(db):
    metrics = MetricsResponse(
        files_processed=0,
        min_time_processed=0.0,
        avg_time_processed=0.0,
        max_time_processed=0.0,
        latest_file_processed_timestamp=None
    )
    processed_file_repo = ProcessedFileRepository(db)

    processed_files = processed_file_repo.get_all()

    if not processed_files:
        return metrics

    files_processed = len(processed_files)

    times_processed = [float(file.time_processed) for file in processed_files]
    min_time_processed = min(times_processed)
    avg_time_processed = sum(times_processed) / len(times_processed)
    max_time_processed = max(times_processed)

    latest_file_processed_timestamp = max(file.created_at for file in processed_files).timestamp()

    metrics.files_processed = files_processed
    metrics.min_time_processed = round(min_time_processed, 3)
    metrics.avg_time_processed = round(avg_time_processed, 3)
    metrics.max_time_processed = round(max_time_processed, 3)
    metrics.latest_file_processed_timestamp = latest_file_processed_timestamp


    return metrics
