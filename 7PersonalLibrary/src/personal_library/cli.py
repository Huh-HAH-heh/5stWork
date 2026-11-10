"""Консольный интерфейс личной библиотеки."""

from pathlib import Path

from .library import Library
from .models import Book


def _ask_text(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не должно быть пустым.")


def _ask_int(prompt: str, minimum: int = 0, maximum: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Введите целое число.")
            continue
        if value < minimum or (maximum is not None and value > maximum):
            limit = f"от {minimum}" if maximum is None else f"от {minimum} до {maximum}"
            print(f"Число должно быть {limit}.")
            continue
        return value


def _show_books(books: list[Book]) -> None:
    if not books:
        print("Книги не найдены.")
        return
    for number, book in enumerate(books, start=1):
        print(f"{number}. {book} — {book.pages} стр., жанр: {book.genre}")


def run(library: Library) -> None:
    """Запустить цикл консольного меню."""
    library.load()
    print("=== ЛИЧНАЯ БИБЛИОТЕКА ===")

    while True:
        print(
            "\n1. Добавить книгу\n"
            "2. Показать все книги\n"
            "3. Найти по автору\n"
            "4. Найти по жанру\n"
            "5. Добавить заметку\n"
            "6. Показать заметки\n"
            "7. Добавить статистику за месяц\n"
            "8. Показать общую статистику\n"
            "9. Удалить книгу\n"
            "0. Выход"
        )
        choice = input("Выберите пункт: ").strip()

        try:
            if choice == "1":
                book = Book(
                    title=_ask_text("Название: "),
                    author=_ask_text("Автор: "),
                    year=_ask_int("Год издания: ", minimum=1),
                    genre=_ask_text("Жанр: "),
                    pages=_ask_int("Количество страниц: ", minimum=1),
                )
                library.add_book(book)
                print("Книга добавлена.")
            elif choice == "2":
                _show_books(library.books)
            elif choice == "3":
                _show_books(library.find_by_author(_ask_text("Автор или часть имени: ")))
            elif choice == "4":
                _show_books(library.find_by_genre(_ask_text("Жанр или часть названия: ")))
            elif choice == "5":
                library.add_note(
                    _ask_text("Название книги: "),
                    _ask_text("Заметка: "),
                )
                print("Заметка сохранена.")
            elif choice == "6":
                title = input("Фильтр по названию (Enter — все заметки): ").strip()
                notes = library.get_notes(title or None)
                if not notes:
                    print("Заметок нет.")
                for item in notes:
                    print(f"[{item['date']}] «{item['title']}»: {item['note']}")
            elif choice == "7":
                month = _ask_text("Месяц (например, 2026-11): ")
                books_read = _ask_int("Прочитано книг: ")
                pages_read = _ask_int("Прочитано страниц: ")
                library.add_month_stat(month, books_read, pages_read)
                print("Статистика добавлена.")
            elif choice == "8":
                totals = library.total_stats()
                print(f"Всего прочитано книг: {totals['books_read']}")
                print(f"Всего прочитано страниц: {totals['pages_read']}")
                print("\nСтатистика по месяцам:")
                for item in library.get_stats():
                    print(
                        f"{item['month']}: {item['books_read']} книг, "
                        f"{item['pages_read']} страниц"
                    )
            elif choice == "9":
                title = _ask_text("Название книги для удаления: ")
                print("Книга удалена." if library.remove_book(title) else "Книга не найдена.")
            elif choice == "0":
                library.save()
                print("Библиотека сохранена. До свидания!")
                return
            else:
                print("Выберите пункт меню от 0 до 9.")
        except (ValueError, OSError) as error:
            print(f"Не удалось выполнить операцию: {error}")


def main() -> None:
    """Создать библиотеку в data/ и запустить меню."""
    library = Library(Path.cwd() / "data")
    try:
        run(library)
    except (EOFError, KeyboardInterrupt):
        library.save()
        print("\nБиблиотека сохранена. Работа завершена.")
