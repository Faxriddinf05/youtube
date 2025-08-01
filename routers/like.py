from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from models.like import Like
from models.video import Video
from models.user import User
from models.channel import Channel
from schemas.user import SchemasUser
from schemas.like import SchemasLike, LikeResponse
from utils.database import database
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from routers.auth import get_current_active_user
from functions.like import create_like


like_router = APIRouter()


@like_router.post("/post_like")
async def like_bosish(
    form: SchemasLike,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await create_like(form, db, current_user)
        return {"message": "Like qo'shildi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@like_router.get("/get_like")
async def like_korish(
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        korish = await db.execute(select(Like).where(Like.user_id == current_user.id))
        result = korish.scalars().all()

        if not result:
            raise HTTPException(404, "Like topilmadi !")

        like = (
            select(
                Like.id,
                User.username,
                Channel.name.label("channel_name"),
                Video.title,
                Video.file_path,
                Video.thumbnail_path,
                Video.views,
                Like.is_like,
                Like.created_at,
            )
            .select_from(Like)
            .join(User, User.id == Like.user_id)
            .join(Video, Video.id == Like.video_id)
            .join(Channel, Channel.id == Video.channel_id)
            .where(Like.user_id == current_user.id)
        )
        result = await db.execute(like)
        rows = result.all()

        return [LikeResponse(**row._mapping) for row in rows]

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@like_router.delete("/delete_like")
async def like_ochirish(
    ident: int,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        korish = await db.execute(
            select(Like).where(Like.id == ident, Like.user_id == current_user.id)
        )
        result = korish.scalar()

        if not result:
            raise HTTPException(404, "Sizda bunday like mavjud emas !")

        if result.is_like:
            video_query = await db.execute(
                select(Video).where(Video.id == result.video_id)
            )
            video = video_query.scalar_one_or_none()

            if video:
                video.like_amount = max(video.like_amount - 1, 0)
                db.add(video)

        await db.execute(
            delete(Like).where(Like.id == ident, Like.user_id == current_user.id)
        )
        await db.commit()
        return {"message": "Like o'chirildi."}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}
