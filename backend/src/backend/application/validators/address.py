import re

STREET_PREFIXES: tuple[str, ...] = (
    "мікрорайон",
    "микрорайон",
    "набережна",
    "набережная",
    "провулок",
    "переулок",
    "проспект",
    "бульвар",
    "вулиця",
    "площадь",
    "тупік",
    "тупик",
    "улица",
    "алея",
    "аллея",
    "площа",
    "узвіз",
    "шосе",
    "шоссе",
    "провул.",
    "переул.",
    "бульв.",
    "просп.",
    "площ.",
    "мкрн.",
    "пров.",
    "мкр.",
    "пр-кт",
    "пр-т",
    "наб.",
    "туп.",
    "узв.",
    "вул.",
    "пер.",
    "б-р.",
    "мкрн",
    "бульв",
    "просп",
    "пров",
    "мкр",
    "пл.",
    "ул.",
    "пр.",
    "ал.",
    "ш.",
    "м-н",
    "б-р",
    "б/р",
    "вул",
    "наб",
    "туп",
    "узв",
    "пл",
    "ул",
    "пр",
    "ал",
    "ш",
)

HOUSE_LETTER_RE = re.compile(r"(\d)\s*[-–—]?\s*([а-яёіїєґa-z])", re.IGNORECASE)


def normalize_street(street: str) -> str:
    s = street.strip().lower()
    for prefix in STREET_PREFIXES:
        if s.startswith(prefix):
            rest = s[len(prefix) :]
            if not rest or rest[0] in {" ", ".", ","}:
                s = rest.lstrip(" .,")
                break
    return s.strip()


def normalize_house(house: str) -> str:
    return HOUSE_LETTER_RE.sub(r"\1\2", house.strip().lower())
