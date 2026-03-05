import logging
import re

logger = logging.getLogger(__name__)

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

_escaped_prefixes = sorted(
    (re.escape(p) for p in STREET_PREFIXES), key=len, reverse=True
)
STREET_PREFIX_SQL_RE = f"^({'|'.join(_escaped_prefixes)})(\\s|[.,])+"
HOUSE_LETTER_SQL_RE = r"(\d)\s*[-–—]?\s*([а-яёіїєґa-zA-Z])"
HOUSE_LETTER_SQL_REPL = r"\1\2"


def normalize_street(street: str) -> str:
    s = street.strip().lower()
    for prefix in STREET_PREFIXES:
        if s.startswith(prefix):
            rest = s[len(prefix) :]
            if not rest or rest[0] in {" ", ".", ","}:
                s = rest.lstrip(" .,")
                break
    result = s.strip()
    if result != street.strip().lower():
        logger.info("normalize_street: %r -> %r", street, result)
    return result


def normalize_house(house: str) -> str:
    stripped = house.strip().lower()
    result = HOUSE_LETTER_RE.sub(r"\1\2", stripped)
    if result != stripped:
        logger.info("normalize_house: %r -> %r", house, result)
    return result
