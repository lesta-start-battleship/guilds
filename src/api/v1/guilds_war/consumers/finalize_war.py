from infra.db.database import async_session_maker
from infra.db.models.guild_war import GuildWarRequest, GuildWarRequestHistory, WarStatus
from datetime import datetime, timezone
from sqlalchemy import select

async def finalize_war(id_guild_war: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(GuildWarRequest).where(
                GuildWarRequest.id == id_guild_war,
                GuildWarRequest.status == WarStatus.active
            )
        )
        war = result.scalar_one_or_none()
        if not war:
            print(f"[DB] Active war {id_guild_war} not found — nothing to finalize.")
            return

        # Перенос в историю
        finished_at = datetime.now(timezone.utc)
        session.add(GuildWarRequestHistory(
            war_id=war.id,
            initiator_guild_id=war.initiator_guild_id,
            target_guild_id=war.target_guild_id,
            status=WarStatus.finished,
            created_at=war.created_at,
            finished_at=finished_at
        ))

        await session.delete(war)
        await session.commit()

        print(f"[DB] War {id_guild_war} finalized and moved to history")