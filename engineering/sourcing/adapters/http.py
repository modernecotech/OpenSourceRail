"""Bounded HTTPS reads with an explicit host and credential boundary."""
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_BYTES = 20 * 1024 * 1024
ALLOWED_HOSTS = frozenset({
    "www.worldbank.org", "thedocs.worldbank.org", "www.ecb.europa.eu",
    "developer.digikey.com", "api.digikey.com", "sandbox-api.digikey.com",
    "sv08data.dot.ca.gov", "dot.ca.gov", "www.ungm.org", "help.ungm.org",
    "itp.iq", "www.itp.iq", "mop.gov.iq", "cbi.iq", "www.cbi.iq",
    "www.easycomposites.co.uk", "www.gurit.com", "transitworld.wabtec.com",
    "rail.knorr-bremse.com", "rails.arcelormittal.com", "www.pandrol.com",
    "www.abb.com", "www.elematic.com", "www.liebherr.com", "www.longi.com",
    "www.thermoking.com", "www.skf.com", "cdn.skfmediahub.skf.com",
})
SECRET_KEYS = {"token", "access_token", "client_secret", "api_key", "apikey",
               "password", "authorization", "refresh_token"}


class FetchError(ValueError):
    """A sanitized transport failure; response bodies and credentials are absent."""

    def __init__(self, code, status=None):
        self.code = code
        self.status = status
        super().__init__(code + (" (HTTP " + str(status) + ")" if status else ""))


def validate_url(url, allowed_hosts):
    if not isinstance(url, str) or len(url) > 4096:
        raise FetchError("invalid-source-url")
    value = urlsplit(url)
    host = value.hostname
    if value.scheme != "https" or not host or value.username or value.password:
        raise FetchError("public-https-source-required")
    try:
        port = value.port
    except ValueError:
        raise FetchError("invalid-source-port") from None
    if port not in (None, 443) or host.lower() not in allowed_hosts:
        raise FetchError("source-host-not-allowed")
    if host.lower() == "localhost" or host.lower().endswith((".localhost", ".local", ".internal")):
        raise FetchError("private-hostname-not-allowed")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise FetchError("literal-network-address-not-allowed")
    if any(key.lower() in SECRET_KEYS for key, _ in parse_qsl(value.query)):
        raise FetchError("credentials-not-allowed-in-source-url")
    return value


class _Redirects(HTTPRedirectHandler):
    max_redirections = 5

    def __init__(self, hosts, credentialled=False):
        self.hosts = hosts
        self.credentialled = credentialled

    def redirect_request(self, request, fp, code, message, headers, newurl):
        if self.credentialled:
            raise FetchError("credentialled-redirect-rejected", code)
        validate_url(newurl, self.hosts)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def request(method, url, *, headers=None, body=None, allowed_hosts=ALLOWED_HOSTS,
            timeout=30, max_bytes=MAX_BYTES, transport=None, credentialled=False):
    """Private transport interface shared with the fixed-endpoint OAuth client.

    An injected transport accepts the same keyword arguments and returns
    ``(status, headers, bytes)``. No token or request body is included in errors.
    """
    hosts = frozenset(str(host).lower() for host in allowed_hosts)
    validate_url(url, hosts)
    if not 0 < timeout <= 30 or not 0 < max_bytes <= MAX_BYTES:
        raise FetchError("request-budget-outside-domain")
    try:
        if transport is not None:
            status, response_headers, raw = transport(
                method, url, headers=dict(headers or {}), body=body,
                timeout=timeout, max_bytes=max_bytes)
            if not isinstance(raw, bytes):
                raise FetchError("transport-bytes-required")
            if 300 <= status < 400:
                raise FetchError("redirect-requires-validated-transport", status)
            if not 200 <= status < 300:
                raise FetchError("http-error", status)
            effective_url = url
        else:
            opener = build_opener(_Redirects(hosts, credentialled))
            req = Request(url, data=body, headers=dict(headers or {}), method=method)
            with opener.open(req, timeout=timeout) as response:
                status = response.status
                response_headers = dict(response.headers)
                effective_url = response.url
                validate_url(effective_url, hosts)
                length = response.headers.get("Content-Length")
                if length is not None and int(length) > max_bytes:
                    raise FetchError("source-body-budget-exceeded")
                raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise FetchError("source-body-budget-exceeded")
    except FetchError:
        raise
    except HTTPError as err:
        raise FetchError("http-error", err.code) from None
    except (URLError, TimeoutError, OSError):
        raise FetchError("source-network-unavailable") from None
    except (ValueError, TypeError):
        raise FetchError("invalid-transport-response") from None
    except Exception:
        raise FetchError("transport-failure") from None
    safe_headers = {str(k).lower(): str(v)[:4096] for k, v in response_headers.items()
                    if str(k).lower() in {"content-type", "etag", "last-modified", "date", "retry-after"}}
    return status, safe_headers, raw, effective_url


def fetch(url, *, allowed_hosts=ALLOWED_HOSTS, timeout=30,
          max_bytes=MAX_BYTES, transport=None, headers=None):
    """Retrieve public bytes and filtered metadata, never credentialled data."""
    supplied = dict(headers or {})
    if any(key.lower() not in {"accept", "user-agent"} for key in supplied):
        raise FetchError("public-fetch-header-not-allowed")
    supplied.setdefault("User-Agent", "OpenSourceRail-sourcing/0.6")
    _, metadata, raw, effective_url = request(
        "GET", url, headers=supplied, allowed_hosts=allowed_hosts,
        timeout=timeout, max_bytes=max_bytes, transport=transport)
    return dict(raw=raw, url=effective_url,
                sha256=hashlib.sha256(raw).hexdigest(),
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                content_type=metadata.get("content-type"), headers=metadata)
