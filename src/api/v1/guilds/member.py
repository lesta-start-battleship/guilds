from typing import Annotated, List

from fastapi import APIRouter, Path, Query, status, Depends

from domain.exceptions.guild import GuildNotExistsException
from domain.exceptions.member import MemberInOtherGuildException, MemberNotFoundException, MemberNotHavePermissionException
from domain.exceptions.role import RoleNotFoundException
from domain.exceptions.tag import InvalidTagFormatException
from schemas.base import MessageResponse, Response
from schemas.member import EditMemberRequest, MemberResponse, MemberPagination

from dependencies.services import get_member_service
from dependencies.services import get_guild_service
from services.member_ import MemberService
from services.guild_ import GuildService


from .responses.guild import guild_not_found, uncorrect_guild_tag
from .responses.member import member_is_not_owner, member_not_found, member_in_other_guild, member_not_have_permissoin
from .responses.role import role_not_found

router = APIRouter()

@router.get('/member/{user_id}', response_model=Response[MemberResponse])
async def get_member_by_user_id(
    user_id: Annotated[int, Path(..., description='User ID')],
    member_service: MemberService = Depends(get_member_service)
    ):
    try:
        member = await member_service.get_user_by_id(user_id)
        return Response(
            error_code=status.HTTP_200_OK,
            value=member
        )
    except MemberNotFoundException:
        return MessageResponse(error=MemberNotFoundException.message, error_code=status.HTTP_404_NOT_FOUND)


@router.get('/guild_id/{guild_id}', response_model=Response[List[int]])
async def get_members_by_guild_id(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    member_service: MemberService = Depends(get_member_service)
    ):
    try:
        members = await member_service.get_members_by_guild_id(guild_id)
        return Response(
            error_code=status.HTTP_200_OK,
            value=members
        )
    except GuildNotExistsException:
        return MessageResponse(error=GuildNotExistsException.message, error_code=status.HTTP_404_NOT_FOUND)
    
    
@router.get('/{tag}', response_model=Response[MemberPagination])
async def get_members_by_guild_tag(
    tag: Annotated[str, Path(..., description='Guild tag')],
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(10, ge=1, description='Number of items to return'),
    member_service: MemberService = Depends(get_member_service)
    ):
    try:
        members = await member_service.get_guild_members(tag, limit, offset)
        return Response(
            error_code=status.HTTP_200_OK,
            value=MemberPagination(
                items=members,
                total_items=0,
                total_pages=0
            )
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
        
        
@router.delete('/{tag}/{user_id}', response_model=MessageResponse)
async def delete_member(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_member_id: int,
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        await guild_service.remove_member(tag, user_id,  guild_member_id)
        return Response(
            error_code=status.HTTP_200_OK
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberInOtherGuildException:
        return member_in_other_guild
    except MemberNotHavePermissionException:
        return member_not_have_permissoin


@router.delete('/{tag}/exit/{user_id}', response_model=MessageResponse)
async def exit_from_guild(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        await guild_service.leave_guild(tag, user_id)
        return Response(
            error_code=status.HTTP_200_OK
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberInOtherGuildException:
        return member_in_other_guild
    except MemberNotHavePermissionException:
        return member_not_have_permissoin

    
@router.patch('/{tag}/{user_id}', response_model=Response[MemberResponse])
async def change_member_role(
    tag: Annotated[str, Path(..., description='Guild tag')],
    guild_member_id: int,
    user_id: Annotated[int, Path(..., description='User ID')],
    role_form: EditMemberRequest,
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        member = await guild_service.change_member_role(tag, guild_member_id, user_id, role_form.role_id)
        return Response(
            error_code=status.HTTP_200_OK,
            value=member
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberInOtherGuildException:
        return member_in_other_guild
    except MemberNotHavePermissionException:
        return member_not_have_permissoin
    except RoleNotFoundException:
        role_not_found