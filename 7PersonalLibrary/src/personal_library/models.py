"""Модели данных приложения."""

from dataclasses import dataclass


BOOK_STATUSES = ("не прочитана", "читаю", "прочитана")


@dataclass
class Book:
    """Книга домашней библиотеки."""

    title: str
    author: str
    year: int
    genre: str
    pages: int
    status: str = "не прочитана"
    rating: int | None = None

    def __post_init__(self) -> None:
        if self.status not in BOOK_STATUSES:
            raise ValueError(f"Недопустимый статус книги: {self.status}")
        if self.rating is not None and (
            isinstance(self.rating, bool)
            or not isinstance(self.rating, int)
            or not 1 <= self.rating <= 5
        ):
            raise ValueError("Оценка должна быть целым числом от 1 до 5 или None")

    def to_dict(self) -> dict:
        """Преобразовать книгу в словарь для JSON."""
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "pages": self.pages,
            "status": self.status,
            "rating": self.rating,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Восстановить книгу из словаря; необязательные поля имеют значения по умолчанию."""
        return cls(
            title=data["title"],
            author=data["author"],
            year=int(data["year"]),
            genre=data["genre"],
            pages=int(data["pages"]),
            status=data.get("status", "не прочитана"),
            rating=data.get("rating"),
        )

    def __str__(self) -> str:
        stars = "без оценки" if self.rating is None else "★" * self.rating + "☆" * (5 - self.rating)
        return f"«{self.title}» — {self.author} ({self.year}) [{self.status}] {stars}"
