from typing import Annotated, List
from fastapi import APIRouter, Path, Query, status, Depends

from src.repositories.guild import GuildRepository
from src.dependencies.guild import get_guild_repository, get_member_repository, get_role_repository
from src.repositories.member import MemberRepository
from src.repositories.role import RoleRepository
from src.schemas.guild import GuildResponse, CreateGuildRequest, EditGuildRequest

router = APIRouter()

@router.get('/', response_model=List[GuildResponse])
async def get_guilds(
    guild_repo: GuildRepository = Depends(get_guild_repository),
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(10, ge=1, description='Number of items to return'),
    ):
    guilds = await guild_repo.get_guilds(limit, offset)
    return [
        GuildResponse(
            tag=guild.tag,
            name=guild.name,
            desciption=guild.description,
            id=guild.id,
            owner_id=guild.owner_id
        ) for guild in guilds
    ]
    
    
@router.get('/{guild_id}', response_model=GuildResponse)
async def get_guild_by_id(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    guild_repo: GuildRepository = Depends(get_guild_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    
    if not guild:
        return status.HTTP_404_NOT_FOUND
    
    return GuildResponse(
        tag=guild.tag,
        name=guild.name,
        desciption=guild.description,
        id=guild.id,
        owner_id=guild.owner_id
        )
    
        
@router.get('/tag/{tag}', response_model=GuildResponse)
async def get_guild_by_tag(
    tag: Annotated[int, Path(..., description='Guild tag')],
    guild_repo: GuildRepository = Depends(get_guild_repository)
    ):
    guild = await guild_repo.get_by_tag(tag)
    
    if not guild:
        return status.HTTP_404_NOT_FOUND
    
    return GuildResponse(
        tag=guild.tag,
        name=guild.name,
        desciption=guild.description,
        id=guild.id,
        owner_id=guild.owner_id
        )
    
    
@router.post('/', response_model=GuildResponse)
async def create_guild(
    guild_form: CreateGuildRequest,
    user_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository),
    member_repo: MemberRepository = Depends(get_member_repository),
    role_repo: RoleRepository = Depends(get_role_repository)
    ):
    
    if await guild_repo.get_by_tag(guild_form.tag):
        return status.HTTP_409_CONFLICT
    
    if await member_repo.get_by_user_id(user_id):
        return status.HTTP_409_CONFLICT
        
    new_guild = await guild_repo.create(
        owner_id=user_id,
        tag=guild_form.tag,
        title=guild_form.title,
        description=guild_form.desciption,
        )
    
    if not new_guild:
        status.HTTP_400_BAD_REQUEST
        
    owner = await member_repo.add_member(new_guild.id, user_id, 'Stranger')
    if not owner:
        return status.HTTP_400_BAD_REQUEST
    
    role = await role_repo.get_by_title('owner')
    if not role:
        return status.HTTP_404_NOT_FOUND
    
    if not await member_repo.edit(user_id=owner.user_id, role_id=role.id):
        return status.HTTP_400_BAD_REQUEST
        
    return GuildResponse(
        id=new_guild.id,
        owner_id=new_guild.owner_id,
        tag=new_guild.tag,
        title=new_guild.title,
        desciption=new_guild.description
    )
    
    
@router.delete('/{guild_id}')
async def delete_guild(
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    
    if not guild:
        return status.HTTP_404_NOT_FOUND
    
    if guild.owner_id != user_id:
        return status.HTTP_403_FORBIDDEN
    
    await guild_repo.delete(guild_id)
    return {'status': status.HTTP_200_OK}
    
    
@router.patch('/{guild_id}', response_model=GuildResponse)
async def edit_guild(
    edit_form: EditGuildRequest,
    guild_id: Annotated[int, Path(..., description='Guild ID')],
    user_id: int,
    guild_repo: GuildRepository = Depends(get_guild_repository)
    ):
    guild = await guild_repo.get_by_id(guild_id)
    
    if not guild:
        return status.HTTP_404_NOT_FOUND
    
    if guild.owner_id != user_id:
        return status.HTTP_403_FORBIDDEN
        
    guild = await guild_repo.edit(guild_id, edit_form.title, edit_form.desciption)
    
    return GuildResponse(
        tag=guild.tag,
        name=guild.name,
        desciption=guild.description,
        id=guild.id,
        owner_id=guild.owner_id
        )