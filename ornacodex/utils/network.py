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

`force_ipv4_resolution()` works around this two ways:

1. Patches `socket.getaddrinfo` so any code that looks it up dynamically
   (`socket.getaddrinfo(...)`) only ever sees IPv4 results.
2. Patches `twisted.internet._resolver.GAIResolver` -- the resolver Twisted
   actually uses for the asyncio reactor this project runs on. GAIResolver
   captures `getaddrinfo` as a baked-in default parameter at import time
   (`from socket import getaddrinfo`), so (1) alone never reaches it; the
   default has to be replaced directly on the class.

If `download`/`realm_raids` still aren't reaching playorna.com after this
(but `curl https://playorna.com` works fine from the same machine), the
most reliable fix is at the OS level instead -- e.g. disabling IPv6 system-
wide, or pinning playorna.com to a known-working IPv4 address in
/etc/hosts -- since Scrapy wraps the resolver in another caching layer
(`scrapy.resolver.CachingHostnameResolver`) that this can't fully verify
against every Scrapy/Twisted version.
"""

import socket

_original_getaddrinfo = socket.getaddrinfo
_patched = False


def force_ipv4_resolution() -> None:
    """Make DNS lookups in this process return IPv4 addresses only.

    Idempotent: safe to call more than once.
    """
    global _patched
    if _patched:
        return

    def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = getaddrinfo_ipv4

    try:
        from twisted.internet._resolver import GAIResolver
    except ImportError:
        GAIResolver = None

    if GAIResolver is not None:
        defaults = GAIResolver.__init__.__defaults__
        if defaults:
            GAIResolver.__init__.__defaults__ = tuple(
                getaddrinfo_ipv4 if d is _original_getaddrinfo else d
                for d in defaults
            )

    _patched = True
