from pathlib import Path
from re import search


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def does_string_contains_date(line):
    result = search(r"\d*-\d*-\d*", line)
    return result is not None


def get_date_from_string(line):
    return search(r"\d*-\d*-\d*", line).group().strip()


def get_timestamp_from_string(line: str):
    return search(r"(?<=\])\s*\d*-\d*-\d*\s\d*:\d*:\d*\.?\d*", line).group().strip()


def contains_timestamp_with_ms(line: str):
    return search(r"(?<=\])\s*\d*-\d*-\d*\s\d*:\d*:\d*\.\d*", line) is not None
