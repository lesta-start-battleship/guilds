from typing import Annotated, List
from fastapi import APIRouter, Path, Query, status, Depends

from src.dependencies.guild import get_guild_repository, get_member_repository, get_role_repository
from src.repositories.guild import GuildRepository
from src.repositories.member import MemberRepository
from src.repositories.role import RoleRepository
from src.schemas.member import AddMemberRequest, EditMemberRequest, MemberResponse

router = APIRouter()

@router.get('/member/{user_id}', response_model=MemberResponse)
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
    
    
@router.get('/{guild_id}/member/', response_model=List[MemberResponse])
async def get_members_by_guild_id(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    members = await member_repo.get_by_guild_id(guild_id)
    return [
        MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        role_id=member.role_id,
        guild_id=member.guild_id
        ) for member in members
    ]
    
    
@router.post('/{guild_id}/member/', response_model=MemberResponse)
async def add_member(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    guild_member_id: int,
    member_form: AddMemberRequest,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    if not guild:
        return status.HTTP_404_NOT_FOUND
        
    member = await member_repo.get_by_user_id(member_form.user_id)
    if member:
        return status.HTTP_409_CONFLICT
    
    guild_member = await member_repo.get_by_user_id(guild_member_id)
    if not guild_member or guild_member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(guild_member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    member = await member_repo.add_member(guild_id, member_form.user_id, member_form.user_name)
    return MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        role_id=member.role_id,
        guild_id=member.guild_id
        )
        
        
@router.delete('/{guild_id}/member/{user_id}')
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
    
    guild_member = await member_repo.get_by_user_id(guild_member_id)
    if not guild_member or guild_member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(guild_member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    await member_repo.delete_member(user_id)
    return {'status': status.HTTP_200_OK}
    
    
@router.patch('/{guild_id}/member/{user_id}', response_model=MemberResponse)
async def edit_member(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    guild_member_id: int,
    user_id: Annotated[int, Path(..., description='User ID')],
    edit_form: EditMemberRequest,
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
    
    guild_member = await member_repo.get_by_user_id(guild_member_id)
    if not guild_member or guild_member.guild_id != guild_id:
        return status.HTTP_403_FORBIDDEN
    
    role = await role_repo.get_by_id(guild_member.role_id)
    if not role.edit:
        return status.HTTP_403_FORBIDDEN
    
    member = await member_repo.edit(edit_form.user_id, edit_form.user_name, edit_form.role_id)
    return MemberResponse(
        user_id=member.user_id,
        user_name=member.user_name,
        role_id=member.role_id,
        guild_id=member.guild_id
        )