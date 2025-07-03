from typing import Annotated, List
from fastapi import APIRouter, Path, Query, status, Depends

from dependencies.guild import get_guild_repository, get_member_repository, get_role_repository
from repositories.guild import GuildRepository
from repositories.member import MemberRepository
from repositories.role import RoleRepository
from schemas.member import MemberResponse, AddMemberRequest, EditMemberRequest

router = APIRouter()

@router.get('/{user_id}', response_model=MemberResponse)
async def get_member_by_user_id(
    user_id: Annotated[int, Path(..., description='User ID')],
    member_repo: MemberRepository = Depends(get_guild_repository)
    ):
    member = await member_repo.get_by_user_id(user_id)
    if not member:
        return status.HTTP_404_NOT_FOUND
        
    return MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        role_id=member.role_id,
        guild_id=member.guild_id
        )
    
    
@router.get('/members/{guild_id}', response_model=List[MemberResponse])
async def get_members_by_guild_id(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(10, ge=1, description='Number of items to return'),
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    members = await member_repo.get_by_guild_id(guild_id, limit, offset)
    return [
        MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        role_id=member.role_id,
        guild_id=member.guild_id
        ) for member in members
    ]
        
        
@router.delete('/members/{guild_id}/{user_id}')
async def delete_member(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    guild_member_id: int,
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if not member:
        return status.HTTP_404_NOT_FOUND
    
    if member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    if member.id == guild.owner_id:
        return status.HTTP_403_FORBIDDEN
    
    guild_member = await member_repo.get_by_user_id(guild_member_id)
    if not guild_member or guild_member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(guild_member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    await member_repo.delete_member(user_id)
    return {'status': status.HTTP_200_OK}


@router.delete('/members/{guild_id}/exit')
async def exit_from_guild(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if not member:
        return status.HTTP_404_NOT_FOUND
    
    if member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    if member.id == guild.owner_id:
        return status.HTTP_403_FORBIDDEN
    
    await member_repo.delete_member(user_id)
    return {'status': status.HTTP_200_OK}

    
@router.patch('/members/{guild_id}/{user_id}', response_model=MemberResponse)
async def edit_member(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    guild_member_id: int,
    user_id: Annotated[int, Path(..., description='User ID')],
    edit_form: EditMemberRequest,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if not member:
        return status.HTTP_404_NOT_FOUND
    
    if member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    if guild_member_id != guild.owner_id:
        return status.HTTP_403_FORBIDDEN
    
    member = await member_repo.add_member(guild_id, member_form.user_id, member_form.user_name, role_id=member.role_id)

    return MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        role_id=member.role_id,
        guild_id=member.guild_id
        )


@router.get('/members/requests/{guild_id}')
async def get_requests(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if not member:
        return status.HTTP_404_NOT_FOUND
    
    if member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    requests = await redis.get_requests(guild_id)
    
    return requests
    
    
@router.post('/members/requests/{guild_id}')
async def send_requests(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: int,
    user_form: AddMemberRequest,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository)
    ):
    if await redis.check_request(guild_id, user_id):
        return status.HTTP_409_CONFLICT
    
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if member:
        return status.HTTP_409_CONFLICT
    
    await redis.add_request(guild_id, user_id)
    
    return {'status': status.HTTP_200_OK}
    
    

@router.post('/members/requests/{guild_id}/{user_id}/apply', response_model=MemberResponse)
async def apply_request(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_member_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    if not await redis.check_request(guild_id, user_id):
        return status.HTTP_404_NOT_FOUND
    
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if member:
        return status.HTTP_409_CONFLICT
    
    guild_member = await member_repo.get_by_user_id(guild_member_id)
    if not guild_member or guild_member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(guild_member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    await redis.remove_request(guild_id, user_id)
    
    member = await member_repo.add_member(guild_id, user_id, 'user_name')
    
    return {'status': status.HTTP_200_OK}

@router.delete('/members/requests/{guild_id}/{user_id}/cancel')
async def cancel_request(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: Annotated[int, Path(..., description='User ID')],
    guild_member_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    if not await redis.check_request(guild_id, user_id):
        return status.HTTP_404_NOT_FOUND
    
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(user_id)
    if member:
        return status.HTTP_409_CONFLICT
    
    guild_member = await member_repo.get_by_user_id(guild_member_id)
    if not guild_member or guild_member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(guild_member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    await redis.remove_request(guild_id, user_id)
    
    return {'status': status.HTTP_200_OK}

  
# @router.get('/members/invites')
# async def get_invites(
#     guild_id: Annotated[int, Path(..., description='Guild ID')],
#     user_id: int,
#     guild_repo: GuildRepository = Depends(get_guild_repository),
#     member_repo: MemberRepository = Depends(get_member_repository),
#     role_repo: RoleRepository = Depends(get_role_repository)
#     ):
#     ...
    
    
# @router.post('/members/invites/{guild_id}/{user_id}')
# async def send_invite(
#     guild_id: Annotated[int, Path(..., description='Guild ID')],
#     user_id: Annotated[int, Path(..., description='User ID')],
#     guild_member_id: int,
#     guild_repo: GuildRepository = Depends(get_guild_repository),
#     member_repo: MemberRepository = Depends(get_member_repository),
#     role_repo: RoleRepository = Depends(get_role_repository)
#     ):
#     ...
  
  
# @router.post('members/invite/{guild_id}/apply') 
# async def apply_invite(
#     guild_id: Annotated[int, Path(..., description='Guild ID')],
#     user_id: int,
#     guild_repo: GuildRepository = Depends(get_guild_repository),
#     member_repo: MemberRepository = Depends(get_member_repository),
#     role_repo: RoleRepository = Depends(get_role_repository)
#     ):
#     ...
    
    
# @router.delete('/members/invites/{guild_id}/cancel')
# async def cancel_invite(
#     guild_id: Annotated[int, Path(..., description='Guild ID')],
#     user_id: int,
#     guild_repo: GuildRepository = Depends(get_guild_repository),
#     member_repo: MemberRepository = Depends(get_member_repository),
#     role_repo: RoleRepository = Depends(get_role_repository)
#     ):
#     ...