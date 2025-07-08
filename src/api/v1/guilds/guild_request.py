from typing import Annotated

from fastapi import APIRouter, Path, status, Depends
from fastapi.security import HTTPAuthorizationCredentials

from domain.exceptions.guild import GuildIsFullException, GuildNotExistsException
from domain.exceptions.guild_request import RequestAlreadyExistException, RequestNotFoundException
from domain.exceptions.member import MemberAlreadyInGuildException, MemberInOtherGuildException, MemberNotFoundException, MemberNotHavePermissionException
from domain.exceptions.tag import InvalidTagFormatException

from schemas.base import MessageResponse, Response
from schemas.member import AddMemberRequest, MemberResponse
from schemas.guild_request import RequestPagination, RequestResponse

from dependencies.services import get_request_service
from services.guild_request_ import RequestService

from utils.validate_token import http_bearer, validate_token

from .responses.guild import guild_not_found, uncorrect_guild_tag, guild_is_full
from .responses.member import member_already_in_guild, member_not_found, member_not_have_permissoin, member_in_other_guild
from .responses.guild_request import request_already_exists, request_not_found

router = APIRouter()

@router.get('/{tag}', response_model=Response[RequestPagination])
async def get_requests(
    tag: Annotated[str, Path(..., description='Guild tag')],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        payload = await validate_token(token)
        requests = await request_service.get_requests_by_guild_tag(tag, int(payload['sub']))
        return Response(
            error_code=status.HTTP_200_OK,
            value=RequestPagination(
                items=requests,
                total_items=len(requests),
                total_pages=1
            )
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


@router.post('/{tag}', response_model=Response[RequestResponse])
async def send_request(
    tag: Annotated[str, Path(..., description='Guild tag')],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        payload = await validate_token(token)
        req = await request_service.add_request(tag, int(payload['sub']), payload['username'])
        return Response(
            error_code=status.HTTP_201_CREATED,
            value=req
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except RequestAlreadyExistException:
        return request_already_exists
    except MemberAlreadyInGuildException:
        return member_already_in_guild
    

@router.post('/{tag}/{user_id}/apply', response_model=Response[MemberResponse])
async def apply_request(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        payload = await validate_token(token)
        member = await request_service.apply_request(tag, int(payload['sub']), user_id)
        return Response(
            error_code=status.HTTP_201_CREATED,
            value=member
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberNotHavePermissionException:
        return member_not_have_permissoin
    except RequestNotFoundException:
        return request_not_found
    except GuildIsFullException:
        return guild_is_full
    except MemberAlreadyInGuildException:
        return member_already_in_guild


@router.delete('/{tag}/{user_id}/cancel', response_model=MessageResponse)
async def cancel_request(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        payload = await validate_token(token)
        await request_service.cancel_request(tag, int(payload['sub']), user_id)
        return MessageResponse(
            error_code=status.HTTP_200_OK
        )
    except InvalidTagFormatException:
        return uncorrect_guild_tag
    except GuildNotExistsException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberNotHavePermissionException:
        return member_not_have_permissoin
    except RequestNotFoundException:
        return request_not_found
    except MemberAlreadyInGuildException:
        return member_already_in_guild