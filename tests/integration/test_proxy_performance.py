from statistics import quantiles
from time import perf_counter
import asyncio
from concurrent.futures import ThreadPoolExecutor
import tracemalloc

import httpx

from auth_entry_portal.services.downstream_service import _clients
from auth_entry_portal.services.proxy_http_service import limited_request_stream, limited_response_stream
from tests.conftest import launch_proxy


def test_proxy_p95_added_latency_under_half_second(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    direct_times = []
    proxy_times = []
    with httpx.Client() as direct:
        for _ in range(20):
            started = perf_counter()
            assert direct.get(proxy_service + "/api/data").status_code == 200
            direct_times.append(perf_counter() - started)
            started = perf_counter()
            assert client.get(origin + "/api/data").status_code == 200
            proxy_times.append(perf_counter() - started)
    direct_p95 = quantiles(direct_times, n=20)[18]
    proxy_p95 = quantiles(proxy_times, n=20)[18]
    assert proxy_p95 - direct_p95 < 0.5
    assert _clients


def test_fifty_mb_upload_and_hundred_mb_download(client, csrf, proxy_service):
    origin = launch_proxy(client, csrf)
    block = b"u" * (1024 * 1024)

    def upload_chunks():
        for _ in range(50):
            yield block

    upload = client.post(origin + "/upload", content=upload_chunks())
    assert upload.status_code == 200
    assert upload.json()["size"] == 50 * 1024 * 1024
    download = client.get(origin + f"/download?size={100 * 1024 * 1024}")
    assert download.status_code == 200
    assert len(download.content) == 100 * 1024 * 1024


def test_stream_iterators_do_not_buffer_fifty_or_hundred_mb():
    block = b"x" * (1024 * 1024)

    class RequestStream:
        async def stream(self):
            for _ in range(50):
                yield block

    class ResponseStream:
        async def aiter_raw(self):
            for _ in range(100):
                yield block

    async def consume():
        request_size = 0
        async for chunk in limited_request_stream(RequestStream(), 50 * 1024 * 1024):
            request_size += len(chunk)
        response_size = 0
        async for chunk in limited_response_stream(ResponseStream(), 100 * 1024 * 1024):
            response_size += len(chunk)
        return request_size, response_size

    tracemalloc.start()
    # The full suite keeps a live-server loop active on the main test thread.
    # Run this isolated iterator probe on its own loop without affecting it.
    with ThreadPoolExecutor(max_workers=1) as executor:
        sizes = executor.submit(asyncio.run, consume()).result()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert sizes == (50 * 1024 * 1024, 100 * 1024 * 1024)
    assert peak < 5 * 1024 * 1024
