from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy import delete
from sqlalchemy.future import select
from utils.database import database
from models.user import User
from schemas.user import SchemasUser, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from routers.auth import get_current_active_user
from functions.user import create_user, create_photo, update_user, update_photo

user_router = APIRouter()


@user_router.post("/post_user")
async def royxatdan_otish(form: SchemasUser, db: AsyncSession = Depends(database)):
    try:
        await create_user(form, db)
        return {"message": "Foydananuvchi qo'shildi !"}
    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@user_router.post("/post_image")
async def rasm_yuklash(
    image: UploadFile,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await create_photo(image, db, current_user)
        return {"message": "Rasm yuklandi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@user_router.get("/get_user")
async def royxat_korish(
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    user = await db.execute(select(User).where(User.email == current_user.email))
    result = user.scalar()

    if not result:
        raise HTTPException(404, "Foydalanuvchi topilmadi !")

    return UserResponse(
        username=result.username,
        email=result.email,
        password=result.password,
        create_at=result.create_at,
        image=result.image,
        id=result.id,
    )


@user_router.put("/put_user")
async def royxat_tahrirlash(
    form: SchemasUser,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await update_user(form, db, current_user)
        return {"message": "Foydalanuvchi tahrirlandi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@user_router.put("/put_image")
async def rasm_tahrirlash(
    image: UploadFile,
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await update_photo(image, db, current_user)
        return {"message": "Rasm tahrirlandi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}


@user_router.delete("/delete_user")
async def foydalanuvchi_ochirish(
    db: AsyncSession = Depends(database),
    current_user: SchemasUser = Depends(get_current_active_user),
):
    try:
        await db.execute(delete(User).where(User.id == current_user.id))
        await db.commit()
        return {"message": "Foydalanuvchi o'chirildi !"}

    except Exception as err:
        return {"message": "Xatolik bor!", "Error": str(err)}
