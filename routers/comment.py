from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from models.comment import Comment
from models.video import Video
from models.user import User
from schemas.user import SchemasUser
from schemas.comment import SchemasComment, CommentResponse
from utils.database import database
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from routers.auth import get_current_active_user
from functions.comment import create_comment, update_comment
from utils.check import check_comment_user, check_comment_join

comment_router = APIRouter()


@comment_router.post("/post_comment")
async def izoh_yozish(
    form: SchemasComment,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await create_comment(form, db, current_user)
        return {"message": "Izoh yozildi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@comment_router.get("/get_join")
async def izoh_korish(
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await check_comment_join(db, Comment, current_user)

        comment = (
            select(
                Comment.id,
                User.username,
                User.image,
                Video.file_path,
                Comment.comment,
                Comment.created_at,
            )
            .select_from(Comment)
            .join(User, User.id == Comment.user_id)
            .join(Video, Video.id == Comment.video_id)
            .where(Comment.user_id == current_user.id)
        )

        natija = await db.execute(comment)
        rows = natija.all()

        return [CommentResponse(**row._mapping) for row in rows]

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@comment_router.put("/put_comment")
async def izoh_tahrirlash(
    form: SchemasComment,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await update_comment(form, db, current_user)
        return {"message": "Izoh tahrirlandi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@comment_router.delete("/delete_comment")
async def izoh_ochirish(
    comment_id: int,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await check_comment_user(db, comment_id, Comment, current_user)

        await db.execute(delete(Comment).where(Comment.id == comment_id))
        await db.commit()
        return {"message": "Izoh o'chirildi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}
