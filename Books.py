from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
    {'title': 'JAVA', 'author': 'Arche', 'category': 'Coding'},
    {'title': 'PYTHON', 'author': 'Gabriel', 'category': 'Coding'},
    {'title': 'AWS', 'author': 'Elsa', 'category': 'Cloud'},
    {'title': 'AI/ML Handout', 'author': 'Arche', 'category': 'AI'},
    {'title': 'FASTAPI', 'author': 'Shweta', 'category': 'API'},
    {'title': 'RENDER', 'author': 'Doramii', 'category': 'Hosting'}
]


@app.get("/api-endpoint")
async def first_api():
    return {"message": "Hello Arche!"}

@app.get("/books")
async def get_all_books():
    return BOOKS

##Path Parameter
@app.get("/books/title/{book_title}")
async def get_book(book_title : str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book

#Query Parameter
@app.get("/books/")
async def get_books_by_category(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

##Path Parameter and Query Parameter
@app.get("/books/{book_author}/")
async def get_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for books in BOOKS:
        if books.get('author').casefold() == book_author.casefold() and books.get('category').casefold() == category.casefold():
            books_to_return.append(books)
    return books_to_return

## Post
@app.post("/books/create_books")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

## Put
@app.put("/books/update_book")
async def update_book( updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i].update(updated_book)

## Delete
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            BOOKS.remove(book)

## Assignement (Getting a all the books by the same author)
@app.get("/books/author/{book_author}")
async def get_book_by_author(book_author: str):
    books_to_return = []
    for books in BOOKS:
        if books.get('author').casefold() == book_author.casefold():
            books_to_return.append(books)
    return books_to_return