import pytest

from personal_library import Book, Library


@pytest.fixture
def data_dir(tmp_path):
    """Изолированная временная папка для файлов библиотеки."""
    return tmp_path / "data"


@pytest.fixture
def library(data_dir):
    """Пустая библиотека, не использующая настоящую папку data/."""
    result = Library(data_dir)
    result.load()
    return result


@pytest.fixture
def sample_book():
    return Book("Война и мир", "Лев Толстой", 1869, "Роман", 1225, "прочитана", 5)


@pytest.fixture
def library_with_books(library):
    library.add_book(Book("Война и мир", "Лев Толстой", 1869, "Роман", 1225))
    library.add_book(Book("Преступление и наказание", "Фёдор Достоевский", 1866, "Роман", 671))
    return library
