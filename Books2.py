from asyncio.windows_events import NULL
from typing import Optional

from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app =FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: float
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: float= Field(gt=-1, lt=6)
    published_date: int= Field(gt=1990, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Arche",
                "description": "A new description of the new book",
                "rating": 3.5,
                "published_date": 2026
            }
        }
    }



Books = [
    Book(1, "Computer Science Pro", "Arche", "A very nice book", 3.5, published_date=2025),
    Book(2, "Be fast with FastAPI", "Gabriel", "A great book", 4.2, published_date=2020),
    Book(3, "Master Endpoints", "Arche", "An awesome book", 4, published_date=2023),
    Book(4, "Getting started with JAVA", "Elsa", "Beginner friendly JAVA", 5, published_date=2023),
    Book(5, "History and civics", "Shweta", "A detailed book for Indian history", 4.2, published_date=2020),
    Book(6, "The art of medicinal drugs", "Doramii", "A PHD level book for detailed proceedings", 5, published_date=2023),
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def get_books():
    return Books

## Assignment new get request to filter by published_date
@app.get("/books/published/{book_published_date}", status_code=status.HTTP_200_OK)
async def get_book_published(book_published_date: int = Path(gt=1990, lt=2031)):
    books_to_return = []
    for book in Books:
        if book.published_date == book_published_date:
            books_to_return.append(book)
    if books_to_return == []:
        raise HTTPException(status_code=404, detail="Book not found")
    else:
        return books_to_return

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in Books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating: float = Query(gt=-1, lt=6)):
    books_to_return = []
    for book in Books:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.post("/create-books", status_code=status.HTTP_201_CREATED)
async def create_books(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    Books.append(find_book_id(new_book))

def find_book_id(book: Book):
    if len(Books) > 0:
        book.id = Books[-1].id +1
    else:
        book.id = 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_202_ACCEPTED)
async def update_books(book: BookRequest):
    book_changed= False
    for i in range(len(Books)):
        if Books[i].id == book.id:
            Books[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(Books)):
        if Books[i].id == book_id:
            Books.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")
