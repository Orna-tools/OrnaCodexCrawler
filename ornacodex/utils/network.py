"""Network-related workarounds.

Some hosts -- notably some CI/self-hosted-runner boxes -- advertise IPv6 DNS
records for a domain but have no actual route to the internet over IPv6, so
connection attempts to those addresses fail immediately with "Network is
unreachable". Tools like curl notice the failure and immediately fall back
to a working IPv4 address ("Happy Eyeballs"), but Twisted (which Scrapy
runs on) doesn't reliably do the same, especially when the IPv6 failure is
instant rather than a slow timeout -- so every request can silently die
before it ever leaves the box, even though the site is perfectly reachable
over IPv4.

`force_ipv4_resolution()` works around this by making every DNS lookup in
this process return IPv4 addresses only, so Twisted/Scrapy never attempts
the broken IPv6 path in the first place. Enable it with `--force-ipv4` (see
main.py) if `download`/`realm_raids` aren't reaching playorna.com but
`curl https://playorna.com` works fine from the same machine.
"""

import socket

_original_getaddrinfo = socket.getaddrinfo
_patched = False


def force_ipv4_resolution() -> None:
    """Monkeypatch `socket.getaddrinfo` to only ever return IPv4 results.

    Idempotent: safe to call more than once.
    """
    global _patched
    if _patched:
        return

    def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = getaddrinfo_ipv4
    _patched = True
