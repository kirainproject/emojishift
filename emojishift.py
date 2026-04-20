import hashlib
import json
import os

_EMOJI_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all-emoji.json")
_emoji_list: list = []
_emoji_to_index: dict = {}

NOISE_COUNT = 2   # noise emoji per karakter asli
ASCII_BASE = 32   # printable ASCII mulai dari spasi
ASCII_RANGE = 95  # spasi (32) sampai ~ (126)


def _load():
    global _emoji_list, _emoji_to_index
    if _emoji_list:
        return
    if not os.path.exists(_EMOJI_DB_PATH):
        raise FileNotFoundError(f"all-emoji.json not found at {_EMOJI_DB_PATH}")
    with open(_EMOJI_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "id" in item and "emoji" in item:
                entries.append((int(item["id"]), item["emoji"]))
            elif isinstance(item, list) and len(item) >= 3:
                try:
                    entries.append((int(item[0]), item[2]))
                except (ValueError, IndexError):
                    pass
    elif isinstance(data, dict):
        for k, v in data.items():
            try:
                entries.append((int(k), v if isinstance(v, str) else v["emoji"]))
            except (ValueError, KeyError):
                pass
    entries.sort(key=lambda x: x[0])
    _emoji_list = [e for _, e in entries]
    _emoji_to_index = {e: i for i, e in enumerate(_emoji_list)}


def total() -> int:
    _load()
    return len(_emoji_list)


def _noise_emojis(password: str, char_index: int) -> list:
    """Generate NOISE_COUNT emoji noise deterministik dari password + index."""
    n = len(_emoji_list)
    result = []
    for j in range(NOISE_COUNT):
        seed = f"{password}:{char_index}:{j}".encode()
        h = int(hashlib.sha256(seed).hexdigest(), 16)
        result.append(_emoji_list[h % n])
    return result


def encrypt(text: str, password: str) -> str:
    _load()
    if not password:
        raise ValueError("Password cannot be empty")
    n = len(_emoji_list)
    shifts = [ord(c) for c in password]
    out = []
    for i, ch in enumerate(text):
        # shift dalam ruang printable ASCII (mod 95), map ke emoji
        idx = ((ord(ch) - ASCII_BASE) + shifts[i % len(shifts)]) % ASCII_RANGE
        real = _emoji_list[idx % n]
        noise = _noise_emojis(password, i)
        out.append(real)
        out.extend(noise)
    return "".join(out)


def decrypt(cipher: str, password: str) -> str:
    _load()
    if not password:
        raise ValueError("Password cannot be empty")
    shifts = [ord(c) for c in password]

    tokens = list(cipher)

    result = []
    step = 1 + NOISE_COUNT
    for i, tok_idx in enumerate(range(0, len(tokens), step)):
        if tok_idx >= len(tokens):
            break
        tok = tokens[tok_idx]
        if tok not in _emoji_to_index:
            result.append(tok)
            continue
        idx = (_emoji_to_index[tok] - shifts[i % len(shifts)]) % ASCII_RANGE
        result.append(chr(idx + ASCII_BASE))
    return "".join(result)