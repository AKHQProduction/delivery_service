import re


def is_contains_emoji(text: str) -> bool:
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"
        "\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff"
        "\U0001f700-\U0001f77f"
        "\U0001f780-\U0001f7ff"
        "\U0001f800-\U0001f8ff"
        "\U0001f900-\U0001f9ff"
        "\U0001fa00-\U0001fa6f"
        "\U0001fa70-\U0001faff"
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return bool(emoji_pattern.search(text))


def is_address_specific_enough(address: str) -> bool:
    words = address.split()
    max_keywords = 2
    keywords = [
        "вул.",
        "вулиця",
        "бульвар",
        "бул.",
        "проспект",
        "площа",
        "пров.",
        "провулок",
    ]

    if any(keyword in address.lower() for keyword in keywords):
        for idx, word in enumerate(words):
            if word in keywords:
                words.pop(idx)

        if len(words) < max_keywords:
            return False

    if not any(re.search(r"\d+", word) for word in words):
        return False

    return (
        not sum(address.lower().count(keyword) for keyword in keywords)
        >= max_keywords
    )
