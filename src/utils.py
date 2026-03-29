import datetime
import http.client


def get_iso_datetime() -> str:
	return datetime.datetime.now(datetime.UTC).isoformat()


def has_internet_connection(dns='1.1.1.1', timeout=5, imitate: bool | None = None) -> bool:
	if imitate is not None:
		return imitate

	conn = http.client.HTTPSConnection(dns, timeout=timeout)
	try:
		conn.request('HEAD', '/')
		return True
	except Exception:
		return False
	finally:
		conn.close()
