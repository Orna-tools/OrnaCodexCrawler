import socket

import ornacodex.utils.network as network


def test_force_ipv4_resolution_filters_out_ipv6(monkeypatch):
    # Mirrors playorna.com's real DNS response: both AAAA and A records.
    mixed_results = [
        (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2606:4700:20::681a:72', 443, 0, 0)),
        (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2606:4700:20::ac43:4418', 443, 0, 0)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('104.26.0.114', 443)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('104.26.1.114', 443)),
    ]

    def fake_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if family == socket.AF_INET:
            return [r for r in mixed_results if r[0] == socket.AF_INET]
        return mixed_results

    monkeypatch.setattr(network, '_original_getaddrinfo', fake_getaddrinfo)
    monkeypatch.setattr(network, '_patched', False)

    network.force_ipv4_resolution()
    try:
        results = socket.getaddrinfo('playorna.com', 443)
        families = {r[0] for r in results}
        assert families == {socket.AF_INET}
        assert len(results) == 2
    finally:
        socket.getaddrinfo = network._original_getaddrinfo


def test_force_ipv4_resolution_is_idempotent(monkeypatch):
    monkeypatch.setattr(network, '_patched', False)
    network.force_ipv4_resolution()
    patched_fn = socket.getaddrinfo
    network.force_ipv4_resolution()
    assert socket.getaddrinfo is patched_fn
    socket.getaddrinfo = network._original_getaddrinfo


def test_force_ipv4_resolution_patches_gairesolver_default(monkeypatch):
    """Regression test: socket.getaddrinfo alone never reaches Twisted's
    actual resolver for the asyncio reactor, since GAIResolver captures
    `getaddrinfo` as a baked-in __init__ default at import time. Twisted's
    base.py instantiates it with no explicit getaddrinfo arg
    (`_GAIResolver(reactor, self.getThreadPool)`), so the default has to
    actually be patched for this to work in practice.
    """
    from twisted.internet._resolver import GAIResolver

    monkeypatch.setattr(network, '_patched', False)
    network.force_ipv4_resolution()
    try:
        class FakeReactor:
            def getThreadPool(self):
                return None

        # Mirrors exactly how twisted/internet/base.py:_initThreads() calls it
        resolver = GAIResolver(FakeReactor(), FakeReactor().getThreadPool)
        assert resolver._getaddrinfo is not network._original_getaddrinfo
        assert resolver._getaddrinfo.__name__ == 'getaddrinfo_ipv4'
    finally:
        socket.getaddrinfo = network._original_getaddrinfo
