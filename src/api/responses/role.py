from fastapi import status

from schemas.base import Response

role_not_found = Response(
    error='Указанная роль не найдена',
    error_code=status.HTTP_404_NOT_FOUND
)