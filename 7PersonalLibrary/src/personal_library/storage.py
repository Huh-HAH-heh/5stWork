"""Функции хранения данных в JSON, TXT и CSV."""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable


NOTE_PATTERN = re.compile(
    r"^\[(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] "
    r"«(?P<title>.*?)»: (?P<note>.*)$"
)
STAT_FIELDS = ["month", "books_read", "pages_read"]


def _prepare_parent(filepath: str | Path) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_books_json(books_dicts: Iterable[dict], filepath: str | Path) -> None:
    """Сохранить список словарей книг в JSON."""
    path = _prepare_parent(filepath)
    with path.open("w", encoding="utf-8") as file:
        json.dump(list(books_dicts), file, ensure_ascii=False, indent=2)


def load_books_json(filepath: str | Path) -> list[dict]:
    """Загрузить книги; если файла ещё нет, вернуть пустой список."""
    path = Path(filepath)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("Файл каталога книг должен содержать JSON-список")
    return data


def append_note(filepath: str | Path, title: str, note: str) -> None:
    """Добавить заметку с текущими датой и временем."""
    path = _prepare_parent(filepath)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with path.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] «{title}»: {note}\n")


def read_all_notes(filepath: str | Path) -> list[dict[str, str]]:
    """Прочитать корректные заметки, пропуская строки неверного формата."""
    path = Path(filepath)
    if not path.exists():
        return []

    notes = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            match = NOTE_PATTERN.match(line.rstrip("\r\n"))
            if match:
                notes.append(match.groupdict())
    return notes


def append_month_stat(
    filepath: str | Path, month: str, books_read: int, pages_read: int
) -> None:
    """Добавить статистику за месяц, создав заголовок при необходимости."""
    path = _prepare_parent(filepath)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=STAT_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(
            {
                "month": month,
                "books_read": int(books_read),
                "pages_read": int(pages_read),
            }
        )


def read_stats(filepath: str | Path) -> list[dict[str, str | int]]:
    """Прочитать месячную статистику, преобразовав счётчики в int."""
    path = Path(filepath)
    if not path.exists():
        return []

    stats = []
    with path.open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            try:
                stats.append(
                    {
                        "month": row["month"],
                        "books_read": int(row["books_read"]),
                        "pages_read": int(row["pages_read"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                # Повреждённая строка статистики не мешает чтению остальных.
                continue
    return stats
