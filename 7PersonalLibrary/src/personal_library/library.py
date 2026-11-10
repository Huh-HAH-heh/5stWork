"""Бизнес-логика домашней библиотеки."""

from pathlib import Path

from .models import Book
from . import storage


class Library:
    """Управляет книгами, заметками и статистикой, делегируя файлы storage."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.books_file = self.data_dir / "books.json"
        self.notes_file = self.data_dir / "notes.txt"
        self.stats_file = self.data_dir / "reading_stats.csv"
        self.books: list[Book] = []

    def add_book(self, book: Book) -> None:
        """Добавить книгу и сразу сохранить каталог."""
        self.books.append(book)
        self.save()

    def remove_book(self, title: str) -> bool:
        """Удалить первую книгу с таким названием без учёта регистра."""
        search_title = title.casefold()
        for index, book in enumerate(self.books):
            if book.title.casefold() == search_title:
                del self.books[index]
                self.save()
                return True
        return False

    def find_by_author(self, author: str) -> list[Book]:
        """Найти книги по частичному совпадению автора без учёта регистра."""
        query = author.casefold().strip()
        if not query:
            return []
        return [book for book in self.books if query in book.author.casefold()]

    def find_by_genre(self, genre: str) -> list[Book]:
        """Найти книги по частичному совпадению жанра без учёта регистра."""
        query = genre.casefold().strip()
        if not query:
            return []
        return [book for book in self.books if query in book.genre.casefold()]

    def save(self) -> None:
        """Сохранить текущий каталог книг."""
        storage.save_books_json((book.to_dict() for book in self.books), self.books_file)

    def load(self) -> None:
        """Загрузить каталог и восстановить объекты Book."""
        self.books = [Book.from_dict(data) for data in storage.load_books_json(self.books_file)]

    def add_note(self, title: str, note: str) -> None:
        storage.append_note(self.notes_file, title, note)

    def get_notes(self, filter_title: str | None = None) -> list[dict[str, str]]:
        notes = storage.read_all_notes(self.notes_file)
        if filter_title is None:
            return notes
        query = filter_title.casefold().strip()
        return [item for item in notes if query in item["title"].casefold()]

    def add_month_stat(self, month: str, books_read: int, pages_read: int) -> None:
        storage.append_month_stat(self.stats_file, month, books_read, pages_read)

    def get_stats(self) -> list[dict[str, str | int]]:
        return storage.read_stats(self.stats_file)

    def total_stats(self) -> dict[str, int]:
        """Вернуть суммарное количество прочитанных книг и страниц."""
        stats = self.get_stats()
        return {
            "books_read": sum(int(item["books_read"]) for item in stats),
            "pages_read": sum(int(item["pages_read"]) for item in stats),
        }
