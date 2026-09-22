import asyncio
import statistics
import time
import httpx
from tabulate import tabulate if False else None


async def benchmark_endpoint(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    payload: dict = None,
    headers: dict = None,
    total_requests: int = 50,
    concurrency: int = 10
):
    semaphore = asyncio.Semaphore(concurrency)
    latencies = []
    status_codes = []
    errors = 0

    async def single_request():
        nonlocal errors
        async with semaphore:
            t0 = time.perf_counter()
            try:
                if method.upper() == "GET":
                    resp = await client.get(url, headers=headers)
                else:
                    resp = await client.post(url, json=payload, headers=headers)
                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000)
                status_codes.append(resp.status_code)
            except Exception:
                errors += 1

    tasks = [single_request() for _ in range(total_requests)]
    start = time.perf_counter()
    await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start

    if not latencies:
        return {"error": "All requests failed"}

    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
    rps = total_requests / total_time

    return {
        "endpoint": f"{method} {url}",
        "total_requests": total_requests,
        "concurrency": concurrency,
        "rps": round(rps, 1),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "errors": errors,
        "success_rate": f"{round((total_requests - errors) / total_requests * 100, 1)}%"
    }


async def main():
    base_url = "http://127.0.0.1:8000"
    print("=" * 60)
    print(f"🚀 ORG-XRAY Performance Benchmark Runner ({base_url})")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        # Pre-flight check
        try:
            r = await client.get("/api/v1/health")
            if r.status_code != 200:
                print(f"[!] Server returned non-200 on /health: {r.status_code}")
                return
        except Exception as e:
            print(f"[!] Unable to reach server at {base_url}: {e}")
            print("    Please ensure API server is running before executing benchmark.")
            return

        print("[*] Running benchmarks on core endpoints...")
        
        benchmarks = [
            ("GET", "/api/v1/health", None),
            ("GET", "/api/v1/metrics", None),
        ]

        results = []
        for method, path, payload in benchmarks:
            res = await benchmark_endpoint(
                client=client,
                method=method,
                url=path,
                payload=payload,
                total_requests=50,
                concurrency=5
            )
            results.append(res)
            print(f"  [+] {res['endpoint']}: {res['rps']} req/s | p50: {res['p50_ms']}ms | p95: {res['p95_ms']}ms | Errors: {res['errors']}")

        print("\n" + "=" * 60)
        print("✅ Benchmark Completed Successfully")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
