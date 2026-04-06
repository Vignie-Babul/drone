import base64


def b64enc(string: str, encoding='ascii') -> bytes:
	return base64.b64encode(string.encode(encoding))


def b64dec(b64_string: bytes, encoding='ascii') -> str:
	return base64.b64decode(b64_string).decode(encoding)
