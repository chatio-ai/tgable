
_VARIATION_SELECTOR_START = 0xfe00
_VARIATION_SELECTOR_END = 0xfe0f
_VARIATION_SELECTOR_RANGE = _VARIATION_SELECTOR_END - _VARIATION_SELECTOR_START

_VARIATION_SELECTOR_SUPPLEMENT_START = 0xe0100
_VARIATION_SELECTOR_SUPPLEMENT_END = 0xe01ef
_VARIATION_SELECTOR_SUPPLEMENT_RANGE = \
        _VARIATION_SELECTOR_SUPPLEMENT_END - _VARIATION_SELECTOR_SUPPLEMENT_START


def decode_text(text: str) -> str:
    result = ''
    buffer = bytearray()
    for char in text:
        code = ord(char)
        if _VARIATION_SELECTOR_START <= code <= _VARIATION_SELECTOR_END:
            buffer.append(code - _VARIATION_SELECTOR_START)
        elif _VARIATION_SELECTOR_SUPPLEMENT_START <= code <= _VARIATION_SELECTOR_SUPPLEMENT_END:
            buffer.append(code - _VARIATION_SELECTOR_SUPPLEMENT_START + _VARIATION_SELECTOR_RANGE)
        else:
            result += buffer.decode()
            buffer.clear()
            result += char

    result += buffer.decode()
    buffer.clear()

    return result


def encode_text(text: str) -> str:
    result: str = ''
    for byte in text.encode():
        if 0 <= byte < _VARIATION_SELECTOR_RANGE:
            result += chr(_VARIATION_SELECTOR_START + byte)
        elif 0 <= byte - _VARIATION_SELECTOR_RANGE < _VARIATION_SELECTOR_SUPPLEMENT_RANGE:
            result += chr(_VARIATION_SELECTOR_SUPPLEMENT_START + byte - _VARIATION_SELECTOR_RANGE)
        else:
            raise ValueError

    return result
