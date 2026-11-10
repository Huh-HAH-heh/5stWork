from personal_library import Book, Library


def test_add_book_persists_after_reload(library, sample_book):
    library.add_book(sample_book)
    another_instance = Library(library.data_dir)
    another_instance.load()
    assert another_instance.books == [sample_book]


def test_remove_book_returns_true_or_false(library_with_books):
    assert library_with_books.remove_book("Война и мир") is True
    assert library_with_books.remove_book("Несуществующая книга") is False


def test_find_by_author_is_case_insensitive(library_with_books):
    found = library_with_books.find_by_author("ТОЛСТ")
    assert len(found) == 1
    assert found[0].author == "Лев Толстой"


def test_find_by_genre_uses_partial_case_insensitive_match(library_with_books):
    assert len(library_with_books.find_by_genre("ром")) == 2


def test_get_notes_can_filter_by_title(library):
    library.add_note("Дюна", "Первая заметка")
    library.add_note("Солярис", "Вторая заметка")
    notes = library.get_notes(filter_title="дюн")
    assert len(notes) == 1
    assert notes[0]["title"] == "Дюна"


def test_total_stats_sums_all_months(library):
    library.add_month_stat("2026-10", 2, 450)
    library.add_month_stat("2026-11", 3, 610)
    assert library.total_stats() == {"books_read": 5, "pages_read": 1060}


def test_load_on_empty_directory_does_not_fail(library):
    library.load()
    assert library.books == []
