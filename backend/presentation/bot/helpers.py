import re


def is_contains_emoji(text: str) -> bool:
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return bool(emoji_pattern.search(text))


def is_address_specific_enough(address: str) -> bool:
    words = address.split()
    keywords = [
        "вул.",
        "вулиця",
        "бульвар",
        "бул.",
        "проспект",
        "площа",
        "пров.",
        "провулок"
    ]

    if any(keyword in address.lower() for keyword in keywords):
        for idx, word in enumerate(words):
            if word in keywords:
                words.pop(idx)

        if len(words) < 2:
            return False

    if not any(re.search(r'\d+', word) for word in words):
        return False

    if sum(address.lower().count(keyword) for keyword in keywords) >= 2:
        return False

    return True
