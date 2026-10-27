import argparse
import shutil
from pathlib import Path

# Старые проверки pathlib оставлены отключёнными.
if False:
    folder = Path("testFiles")
    file = folder / "photo.jpg"
    print(file.exists())
    print(file.suffix)
    print(list(folder.iterdir()))

Ext = {
    ".txt": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".odt": "Documents",
    ".rtf": "Documents",
    ".pdf": "Documents",
    ".md": "Documents",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".tif": "Images",
    ".tiff": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".m4a": "Audio",
    ".wma": "Audio",
    ".mp4": "Video",
    ".mkv": "Video",
    ".avi": "Video",
    ".mov": "Video",
    ".wmv": "Video",
    ".webm": "Video",
    ".mpeg": "Video",
    ".mpg": "Video",
    ".m4v": "Video",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".bz2": "Archives",
    ".xz": "Archives",
    ".tgz": "Archives",
}

Categor = ["Documents", "Images", "Audio", "Video", "Archives", "Other"]
setv = {".DS_Store", "Thumbs.db", "desktop.ini"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Распределяет файлы по папкам в зависимости от расширения."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="папка для сортировки (по умолчанию — текущая)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="показать план действий, не изменяя файлы",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="подробно показывать действия и причины пропуска",
    )
    return parser.parse_args()


def get_category(suffix: str) -> str:
    # Используется последний суффикс: у backup.tar.gz это .gz, поэтому Archives.
    return Ext.get(suffix.lower(), "Other")


def resolve_conflict(dst: Path) -> Path:
    if not dst.exists():
        return dst

    counter = 1
    while True:
        candidate = dst.with_stem(f"{dst.stem}_{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def ensure_folder(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def move_file(source: Path, destination: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(f"Файл не найден: {source}")

    ensure_folder(destination.parent)
    safe_destination = resolve_conflict(destination)

    # Path.rename() может завершиться ошибкой при переносе между файловыми системами.
    # shutil.move() при невозможности переименования использует копирование + удаление.
    shutil.move(source, safe_destination)
    return safe_destination


def organize(directory: Path, dry_run: bool, verbose: bool) -> dict:
    if not directory.exists():
        raise FileNotFoundError(f"Директория не найдена: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Это не директория: {directory}")

    directory = directory.resolve()
    items = list(directory.iterdir())

    stats = {
        "moved": 0,
        "planned": 0,
        "skipped": 0,
        "by_category": {category: 0 for category in Categor},
    }

    # В dry-run ничего не создаём: только рассчитываем предполагаемые пути.
    if not dry_run:
        for category in Categor:
            ensure_folder(directory / category)

    for item in items:
        if not item.is_file():
            continue

        if item.name == Path(__file__).name or item.name in setv:
            stats["skipped"] += 1
            if verbose:
                print(f"Пропущено: {item.name} (служебный файл)")
            continue

        category = get_category(item.suffix)
        destination = directory / category / item.name

        if dry_run:
            result = resolve_conflict(destination)
            stats["planned"] += 1
            stats["by_category"][category] += 1
            print(f"[DRY-RUN] {item.name} -> {result.relative_to(directory)}")
        else:
            result = move_file(item, destination)
            stats["moved"] += 1
            stats["by_category"][category] += 1

            if verbose:
                if result != destination:
                    print(
                        f"Конфликт:   {item.name} -> "
                        f"{result.relative_to(directory)} (переименовано)"
                    )
                else:
                    print(f"Перемещено: {item.name} -> {result.relative_to(directory)}")

    return stats


def print_report(stats: dict, dry_run: bool) -> None:
    for category in Categor:
        print(f"  {category}: {stats['by_category'][category]} файла")

    if dry_run:
        print(f"Планируется переместить: {stats['planned']}")
        print(f"Пропущено: {stats['skipped']}")
        print("Ничего не изменено (режим dry-run).")
    else:
        print(f"Итого перемещено: {stats['moved']}")
        print(f"Пропущено: {stats['skipped']}")


def main() -> None:
    args = parse_args()
    folder = Path(args.directory).expanduser()

    try:
        print(f"Обработка директории: {folder.resolve()}")
        stats = organize(folder, args.dry_run, args.verbose)
        print_report(stats, args.dry_run)
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError) as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
