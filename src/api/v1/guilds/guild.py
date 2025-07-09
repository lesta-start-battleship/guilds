from typing import Annotated

from fastapi import APIRouter, Path, Query, status, Depends
from fastapi.security import HTTPAuthorizationCredentials

from domain.exceptions.guild import GuildAlreadyExistsException, GuildNotExistsException
from domain.exceptions.member import MemberAlreadyInGuildException, MemberNotOwnerException
from domain.exceptions.tag import InvalidTagFormatException
from schemas.base import MessageResponse, Response
from schemas.guild import GuildResponse, CreateGuildRequest, EditGuildRequest, GuildPagination

from services.guild_ import GuildService
from dependencies.services import get_guild_service

from utils.validate_token import http_bearer, validate_token

from .responses.guild import guild_not_found, guild_already_exists, uncorrect_guild_tag
from .responses.member import member_already_in_guild, member_is_not_owner

router = APIRouter()

@router.get('/', response_model=Response[GuildPagination])
async def get_guilds(
    page: int = Query(1, ge=1, description='Number of page'),
    limit: int = Query(10, ge=1, description='Number of items to return'),
    guild_service: GuildService = Depends(get_guild_service)
    ):
    guilds, count = await guild_service.get_guild_list(limit, page)
    return Response(
        error_code=status.HTTP_200_OK if guilds else status.HTTP_204_NO_CONTENT,
        value=GuildPagination(
            items=guilds,
            total_items=count,
            total_pages=(count+limit-1)//limit
        )
    )
 
        
@router.get('/{tag}', response_model=Response[GuildResponse])
async def get_guild_by_tag(
    tag: Annotated[str, Path(..., description='Guild tag')],
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        guild = await guild_service.get_by_tag(tag)
        return Response(
            error_code=status.HTTP_200_OK,
            value=guild
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found


@router.post('/', response_model=Response[GuildResponse])
async def create_guild(
    guild_form: CreateGuildRequest,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        payload = await validate_token(token)
        guild = await guild_service.create_guild(guild_form, int(payload['sub']), payload['username'])
        return Response(
            error_code=status.HTTP_201_CREATED,
            value=guild
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildAlreadyExistsException:
        return guild_already_exists
    except MemberAlreadyInGuildException:
        return member_already_in_guild


@router.delete('/{tag}', response_model=MessageResponse)
async def delete_guild(
    tag: Annotated[str, Path(..., description='Guild tag')],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        payload = await validate_token(token)
        await guild_service.delete_guild(tag, int(payload['sub']))
        return Response(
        error_code=status.HTTP_200_OK
    )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotOwnerException:
        return member_is_not_owner
    
    
@router.patch('/{tag}', response_model=Response[GuildResponse])
async def edit_guild(
    edit_form: EditGuildRequest,
    tag: Annotated[str, Path(..., description='Guild tag')],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    guild_service: GuildService = Depends(get_guild_service)
    ):
    try:
        payload = await validate_token(token)
        guild = await guild_service.edit_guild(tag, int(payload['sub']), edit_form)
        return Response(
            error_code=status.HTTP_200_OK,
            value=guild
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotOwnerException:
        return member_is_not_owner