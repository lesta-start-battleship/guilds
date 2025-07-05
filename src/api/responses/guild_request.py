from fastapi import status

from schemas.base import MessageResponse

request_already_exists = MessageResponse(
    error='Указанный запрос на вступление уже создан',
    error_code=status.HTTP_409_CONFLICT
)

request_not_found = MessageResponse(
    error='Такого запроса не существует',
    error_code=status.HTTP_404_NOT_FOUND
)