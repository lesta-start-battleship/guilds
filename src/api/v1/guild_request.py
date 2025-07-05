from typing import Annotated

from fastapi import APIRouter, Path, status, Depends

from schemas.base import MessageResponse, Response
from schemas.member import MemberResponse
from schemas.guild_request import RequestPagination

from dependencies.services import get_request_service
from services.guild_request import RequestService

from exceptions.guild import UncorrectGuildTagException, GuildNotFoundException, GuildIsFullException
from exceptions.member import MemberAlreadyInGuildException, MemberNotHavePermissionException, MemberNotFoundException, MemberInOtherGuildException
from exceptions.guild_request import RequestAlreadyExistException, RequestNotFoundException

from api.responses.guild import guild_not_found, uncorrect_guild_tag, guild_is_full
from api.responses.member import member_already_in_guild, member_not_found, member_not_have_permissoin
from api.responses.guild_request import request_already_exists, request_not_found

router = APIRouter()

@router.get('/{tag}', response_model=Response[RequestPagination])
async def get_requests(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: int,
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        requests = await request_service.get_requests_by_guild_tag(tag, user_id)
        return Response(
            error_code=status.HTTP_200_OK,
            value=RequestPagination(
                items=requests,
                total_items=len(requests),
                total_pages=0
            )
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberNotHavePermissionException:
        return member_not_have_permissoin


@router.post('/{tag}', response_model=MessageResponse)
async def send_requests(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: int,
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        await request_service.add_request(tag, user_id)
        return MessageResponse(
            error_code=status.HTTP_201_CREATED
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except RequestAlreadyExistException:
        return request_already_exists
    except MemberAlreadyInGuildException:
        return member_already_in_guild
    

@router.post('/{tag}/{user_id}/apply', response_model=Response[MemberResponse])
async def apply_request(
    tag: Annotated[str, Path(..., description='Guild tag')],
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_member_id: int,
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        member = await request_service.apply_request(tag, guild_member_id, user_id)
        return Response(
            error_code=status.HTTP_201_CREATED,
            value=member
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
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
    guild_member_id: int,
    request_service: RequestService = Depends(get_request_service)
    ):
    try:
        await request_service.cancel_request(tag, guild_member_id, user_id)
        return MessageResponse(
            error_code=status.HTTP_200_OK
        )
    except UncorrectGuildTagException:
        return uncorrect_guild_tag
    except GuildNotFoundException:
        return guild_not_found
    except MemberNotFoundException:
        return member_not_found
    except MemberNotHavePermissionException:
        return member_not_have_permissoin
    except RequestNotFoundException:
        return request_not_found
    except MemberAlreadyInGuildException:
        return member_already_in_guild