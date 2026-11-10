from personal_library import Book


def test_to_dict_returns_all_fields(sample_book):
    assert sample_book.to_dict() == {
        "title": "Война и мир",
        "author": "Лев Толстой",
        "year": 1869,
        "genre": "Роман",
        "pages": 1225,
        "status": "прочитана",
        "rating": 5,
    }


def test_from_dict_round_trip(sample_book):
    restored = Book.from_dict(sample_book.to_dict())
    assert restored == sample_book


def test_default_status_and_rating():
    book = Book("Книга", "Автор", 2020, "Фантастика", 300)
    assert book.status == "не прочитана"
    assert book.rating is None


def test_invalid_rating_is_rejected():
    try:
        Book("Книга", "Автор", 2020, "Фантастика", 300, rating=6)
    except ValueError:
        pass
    else:
        raise AssertionError("Ожидалась ошибка для оценки вне диапазона 1–5")
