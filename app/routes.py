from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.auth import authorize, casdoor, get_current_user
from app.database import SessionDep
from app.models import Book
from app.schema import BookDetailsRes, BookReq, BookReqPartial, BookSummaryRes, User

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/callback")
async def auth_callback(code: str, state: str):
    return casdoor.get_oauth_token(code)


@auth_router.get("/profile")
async def auth_profile(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user


book_router = APIRouter(prefix="/books", tags=["Book"])


@book_router.get("/", response_model=list[BookSummaryRes])
async def get_books(session: SessionDep):
    stmt = select(Book)
    return (await session.execute(stmt)).scalars().all()


@book_router.get("/{id}", response_model=BookDetailsRes)
async def get_book(id: int, session: SessionDep):
    book = await session.get(Book, id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return book


@book_router.post(
    "/", response_model=BookDetailsRes, status_code=status.HTTP_201_CREATED
)
async def create_book(
    req: BookReq,
    session: SessionDep,
    user: Annotated[User, Depends(authorize("book", ["write"]))],
):
    book = Book(**req.model_dump())
    book.creator_user_id = book.modifier_user_id = user.id
    session.add(book)
    await session.commit()
    return book


@book_router.put("/{id}", response_model=BookDetailsRes)
async def update_book(
    id: int,
    req: BookReq,
    session: SessionDep,
    user: Annotated[User, Depends(authorize("book", ["write"]))],
):
    book = await session.get(Book, id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    book.patch(**req.model_dump(), modifier_user_id=user.id)
    await session.commit()
    await session.refresh(book)
    return book


@book_router.patch("/{id}", response_model=BookDetailsRes)
async def partial_update_book(
    id: int,
    req: BookReqPartial,
    session: SessionDep,
    user: Annotated[User, Depends(authorize("book", ["write"]))],
):
    book = await session.get(Book, id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    book.patch(**req.model_dump(exclude_unset=True), modifier_user_id=user.id)
    await session.commit()
    await session.refresh(book)
    return book


@book_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    id: int,
    session: SessionDep,
    user: Annotated[User, Depends(authorize("book", ["admin"]))],
):
    book = await session.get(Book, id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await session.delete(book)
    await session.commit()
