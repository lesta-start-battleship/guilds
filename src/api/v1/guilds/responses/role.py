from fastapi import status

from schemas.base import MessageResponse

role_not_found = MessageResponse(
    error='Указанная роль не найдена',
    error_code=status.HTTP_404_NOT_FOUND
)