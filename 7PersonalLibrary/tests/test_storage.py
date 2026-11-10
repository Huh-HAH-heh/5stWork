import csv
from personal_library.storage import (
    append_month_stat,
    append_note,
    load_books_json,
    read_all_notes,
    read_stats,
    save_books_json,
)


def test_json_save_and_load_round_trip(tmp_path):
    path = tmp_path / "nested" / "books.json"
    books = [{"title": "Мастер и Маргарита", "author": "Михаил Булгаков"}]
    save_books_json(books, path)
    assert load_books_json(path) == books


def test_json_missing_file_returns_empty_list(tmp_path):
    assert load_books_json(tmp_path / "missing.json") == []


def test_json_keeps_cyrillic(tmp_path):
    path = tmp_path / "books.json"
    save_books_json([{"title": "Преступление и наказание"}], path)
    assert "Преступление и наказание" in path.read_text(encoding="utf-8")
    assert r"\u" not in path.read_text(encoding="utf-8")


def test_note_is_appended_and_read_with_expected_fields(tmp_path):
    path = tmp_path / "nested" / "notes.txt"
    append_note(path, "Дюна", "Интересный мир и персонажи")
    notes = read_all_notes(path)
    assert len(notes) == 1
    assert notes[0]["title"] == "Дюна"
    assert notes[0]["note"] == "Интересный мир и персонажи"
    assert len(notes[0]["date"]) == 16


def test_multiple_notes_are_read(tmp_path):
    path = tmp_path / "notes.txt"
    append_note(path, "Дюна", "Первая заметка")
    append_note(path, "Солярис", "Вторая заметка")
    assert len(read_all_notes(path)) == 2


def test_broken_note_lines_are_skipped(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text(
        "неверная строка\n[2026-11-10 12:30] «Дюна»: Хорошая книга\n[сломано]\n",
        encoding="utf-8",
    )
    notes = read_all_notes(path)
    assert len(notes) == 1
    assert notes[0]["title"] == "Дюна"


def test_first_csv_write_creates_header(tmp_path):
    path = tmp_path / "stats.csv"
    append_month_stat(path, "2026-10", 2, 450)
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    assert rows[0] == ["month", "books_read", "pages_read"]
    assert rows[1] == ["2026-10", "2", "450"]


def test_second_csv_write_does_not_duplicate_header(tmp_path):
    path = tmp_path / "stats.csv"
    append_month_stat(path, "2026-10", 2, 450)
    append_month_stat(path, "2026-11", 1, 120)
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    assert sum(row == ["month", "books_read", "pages_read"] for row in rows) == 1
    assert len(rows) == 3


def test_csv_numbers_are_integers(tmp_path):
    path = tmp_path / "stats.csv"
    append_month_stat(path, "2026-10", 2, 450)
    stats = read_stats(path)
    assert stats == [{"month": "2026-10", "books_read": 2, "pages_read": 450}]
    assert isinstance(stats[0]["books_read"], int)
    assert isinstance(stats[0]["pages_read"], int)


def test_missing_csv_returns_empty_list(tmp_path):
    assert read_stats(tmp_path / "missing.csv") == []
