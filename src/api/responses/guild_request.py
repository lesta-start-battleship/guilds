from fastapi import status

from schemas.base import Response

request_already_exists = Response(
    error='Указанный запрос на вступление уже создан',
    error_code=status.HTTP_409_CONFLICT
)

request_not_found = Response(
    error='Такого запроса не существует',
    error_code=status.HTTP_404_NOT_FOUND
)