from fastapi import status

from schemas.base import MessageResponse

member_not_found = MessageResponse(
    error='Указанный игрок не состоит в гильдии',
    error_code=status.HTTP_404_NOT_FOUND
    )

member_already_in_guild = MessageResponse(
    error='Указанный игрок уже состит в гильдии',
    error_code=status.HTTP_409_CONFLICT
)

member_is_not_owner = MessageResponse(
    error='Игрок не является владельцем гильдии',
    error_code=status.HTTP_403_FORBIDDEN
)

member_not_have_permissoin = MessageResponse(
    error='У игрока недостаточно прав',
    error_code=status.HTTP_403_FORBIDDEN
)

member_in_other_guild = MessageResponse(
    error='Игрок состоит в другой гильдии',
    error_code=status.HTTP_403_FORBIDDEN
)