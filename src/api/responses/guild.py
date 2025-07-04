from fastapi import status

from schemas.base import Response

uncorrect_guild_tag = Response(
    error='Некорректный формат тега',
    error_code=status.HTTP_400_BAD_REQUEST
)

guild_not_found = Response(
    error='Гильдия с таким тегом не найдена',
    error_code=status.HTTP_404_NOT_FOUND
)

guild_already_exists = Response(
    error='Гильдия с таким тегом уже существует',
    error_code=status.HTTP_409_CONFLICT
)

guild_is_full = Response(
    error='Достигнут лимит участников в гильдии',
    error_code=status.HTTP_403_FORBIDDEN
)