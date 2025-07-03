from fastapi import status

from schemas.base import Response

member_not_found = Response(
    error='Указанный игрок не состоит в гильдии',
    error_code=status.HTTP_404_NOT_FOUND
    )

member_already_in_guild = Response(
    error='Указанный игрок уже состит в гильдии',
    error_code=status.HTTP_409_CONFLICT
)

member_is_not_owner = Response(
    error='Игрок не является владельцем гильдии',
    error_code=status.HTTP_403_FORBIDDEN
)

member_not_have_permissoin = Response(
    error='У игрока недостаточно прав',
    error_code=status.HTTP_403_FORBIDDEN
)

member_in_other_guild = Response(
    error='Игрок состоит в другой гильдии',
    error_code=status.HTTP_403_FORBIDDEN
)