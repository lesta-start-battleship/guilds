from domain.exceptions.member import MemberNotFoundException, MemberNotOwnerException

from services.guild_ import GuildService
from services.guild_request_ import RequestService
from services.member_ import MemberService


class LifecycleService:
    def __init__(self, guild_service: GuildService, member_service: MemberService, request_service: RequestService):
        self.guild_service = guild_service
        self.member_service = member_service
        self.request_service = request_service

    async def on_user_deleted(self, user_id: int):
        try:
            guild = await self.guild_service.get_by_owner_id(user_id)
            await self.guild_service.delete_guild(str(guild.tag), user_id)
            await self.request_service.on_guild_deleted(str(guild.tag))
        except MemberNotOwnerException:
            try:
                member = await self.member_service.get_user_by_id(user_id)
                await self.guild_service.leave_guild(str(member.guild_tag), user_id)
            except MemberNotFoundException:
                await self.request_service.on_user_deleted(user_id)
    
    async def on_username_changed(self, user_id: int, username: str):
        try:
            await self.member_service.get_user_by_id(user_id)
            await self.member_service.on_username_changed(user_id, username)
        except MemberNotFoundException:
            await self.request_service.on_username_changed(user_id, username)