from typing import Annotated

from fastapi import APIRouter, Path, Query, status, Depends

from schemas.base import MessageResponse, Response
from schemas.member import EditMemberRequest, MemberResponse, MemberPagination

from dependencies.services import get_member_service
from services.member import MemberService

from exceptions.guild import UncorrectGuildTagException, GuildNotFoundException
from exceptions.member import MemberNotHavePermissionException, MemberNotFoundException, MemberInOtherGuildException
from exceptions.role import RoleNotFoundException

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
        return member_not_found
    
    
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
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
        
        
@router.delete('/{tag}/{user_id}', response_model=MessageResponse)
async def delete_member(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_member_id: int,
    member_service: MemberService = Depends(get_member_service)
    ):
    try:
        await member_service.delete_member(tag, guild_member_id, user_id)
        return Response(
            error_code=status.HTTP_200_OK
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberNotFoundException:
        return member_is_not_owner
    except MemberInOtherGuildException:
        return member_in_other_guild
    except MemberNotHavePermissionException:
        return member_not_have_permissoin


@router.delete('/{tag}/exit/{user_id}', response_model=MessageResponse)
async def exit_from_guild(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    member_service: MemberService = Depends(get_member_service)
    ):
    try:
        await member_service.exit_from_guild(tag, user_id)
        return Response(
            error_code=status.HTTP_200_OK
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberInOtherGuildException:
        return member_in_other_guild
    except MemberNotHavePermissionException:
        return member_not_have_permissoin

    
@router.patch('/{tag}/{user_id}', response_model=Response[MemberResponse])
async def edit_member(
    tag: Annotated[str, Path(..., description='Guild tag')],
    guild_member_id: int,
    user_id: Annotated[int, Path(..., description='User ID')],
    edit_form: EditMemberRequest,
    member_service: MemberService = Depends(get_member_service)
    ):
    try:
        member = await member_service.edit_member(tag, guild_member_id, user_id, edit_form.role_id)
        return Response(
            error_code=status.HTTP_200_OK,
            value=member
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberNotFoundException:
        return member_is_not_owner
    except MemberInOtherGuildException:
        return member_in_other_guild
    except MemberNotHavePermissionException:
        return member_not_have_permissoin
    except RoleNotFoundException:
        role_not_found