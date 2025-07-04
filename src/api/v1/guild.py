from typing import Annotated
from fastapi import APIRouter, Path, Query, status, Depends

from schemas.base import Response
from schemas.guild import GuildResponse, CreateGuildRequest, EditGuildRequest, GuildPagination
from services.guild import GuildService
from dependencies.services import get_guild_service
from exceptions.guild import UncorrectGuildTagException, GuildNotFoundException, GuildAlreadyExistException
from exceptions.member import MemberIsNotOwnerException, MemberAlreadyInGuildException
from api.responses.guild import guild_not_found, guild_already_exists, uncorrect_guild_tag
from api.responses.member import member_already_in_guild, member_is_not_owner

router = APIRouter()

@router.get('/', response_model=Response[GuildPagination])
async def get_guilds(
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(10, ge=1, description='Number of items to return'),
    guild_service: GuildService = Depends(get_guild_service)
    ):
    guilds = await guild_service.get_guild_list(limit, offset)
    return Response(
        error_code=status.HTTP_200_OK if guilds else status.HTTP_204_NO_CONTENT,
        value=GuildPagination(
            items=guilds,
            total_items=0,
            total_pages=0
        )
    )
 
        
@router.get('/{tag}', response_model=Response[GuildResponse])
async def get_guild_by_tag(
    tag: Annotated[str, Path(..., description='Guild tag')],
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        guild = await guild_service.get_guild_by_tag(tag)
        return Response(
            error_code=status.HTTP_200_OK,
            value=guild
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found


@router.post('/', response_model=Response[GuildResponse])
async def create_guild(
    guild_form: CreateGuildRequest,
    user_id: int,
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        guild = await guild_service.create_guild(guild_form, user_id)
        return Response(
            error_code=status.HTTP_201_CREATED,
            value=guild
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildAlreadyExistException:
        return guild_already_exists
    except MemberAlreadyInGuildException:
        return member_already_in_guild


@router.delete('/{tag}', response_model=Response)
async def delete_guild(
    tag: Annotated[int, Path(..., description='Guild tag')],
    user_id: int,
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        await guild_service.delete_guild(tag, user_id)
        return Response(
        error_code=status.HTTP_200_OK
    )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberIsNotOwnerException:
        return member_is_not_owner
    
    
@router.patch('/{tag}', response_model=Response[GuildResponse])
async def edit_guild(
    edit_form: EditGuildRequest,
    tag: Annotated[int, Path(..., description='Guild tag')],
    user_id: int,
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        guild = await guild_service.edit_guild(tag, user_id, **edit_form)
        return Response(
            error_code=status.HTTP_200_OK,
            value=guild
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberIsNotOwnerException:
        return member_is_not_owner