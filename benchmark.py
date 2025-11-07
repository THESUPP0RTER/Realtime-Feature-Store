#!/usr/bin/env python3
"""
Benchmark script for testing feature store retrieval latency
"""
import requests
import time
import statistics
from typing import List


BASE_URL = "http://localhost:8000"


def register_test_features():
    """Register test features"""
    print("Registering test features...")
    features = [
        {
            "name": "user_age",
            "data_type": "int",
            "entity": "user",
            "ttl_seconds": 3600
        },
        {
            "name": "user_clicks_30d",
            "data_type": "int",
            "entity": "user",
            "ttl_seconds": 3600
        },
        {
            "name": "user_purchases_7d",
            "data_type": "int",
            "entity": "user",
            "ttl_seconds": 3600
        },
        {
            "name": "user_avg_session_time",
            "data_type": "float",
            "entity": "user",
            "ttl_seconds": 3600
        }
    ]

    for feature in features:
        try:
            response = requests.post(f"{BASE_URL}/register", json=feature)
            if response.status_code == 200:
                print(f"  Registered: {feature['name']}")
            else:
                print(f"  Feature {feature['name']} already exists")
        except Exception as e:
            print(f"  Error registering {feature['name']}: {e}")


def ingest_test_data(num_entities: int = 1000):
    """Ingest test data for multiple entities"""
    print(f"\nIngesting test data for {num_entities} entities...")
    for i in range(num_entities):
        entity_id = f"user_{i}"
        data = {
            "entity_id": entity_id,
            "features": [
                {"feature_name": "user_age", "value": 20 + (i % 50)},
                {"feature_name": "user_clicks_30d", "value": 100 + (i % 500)},
                {"feature_name": "user_purchases_7d", "value": i % 20},
                {"feature_name": "user_avg_session_time", "value": 120.5 + (i % 100)}
            ]
        }
        try:
            response = requests.post(f"{BASE_URL}/features/ingest", json=data)
            if response.status_code != 200:
                print(f"  Failed to ingest for {entity_id}")
        except Exception as e:
            print(f"  Error ingesting for {entity_id}: {e}")
    print(f"  Ingested data for {num_entities} entities")


def benchmark_single_entity_retrieval(num_requests: int = 1000) -> List[float]:
    """Benchmark single entity feature retrieval"""
    print(f"\nBenchmarking single entity retrieval ({num_requests} requests)...")

    latencies = []

    for i in range(num_requests):
        entity_id = f"user_{i % 1000}"
        start_time = time.perf_counter()
        try:
            response = requests.get(
                f"{BASE_URL}/features/online/{entity_id}",
                params={"feature_names": "user_age,user_clicks_30d,user_purchases_7d,user_avg_session_time"}
            )
            end_time = time.perf_counter()

            if response.status_code == 200:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        except Exception as e:
            print(f"  ✗ Error in request {i}: {e}")

    return latencies


def benchmark_batch_retrieval(num_requests: int = 100, batch_size: int = 10) -> List[float]:
    """Benchmark batch feature retrieval"""
    print(f"\nBenchmarking batch retrieval ({num_requests} requests, batch size={batch_size})...")

    latencies = []
    feature_names = ["user_age", "user_clicks_30d", "user_purchases_7d", "user_avg_session_time"]

    for i in range(num_requests):
        entity_ids = [f"user_{(i * batch_size + j) % 1000}" for j in range(batch_size)]
        data = {
            "entity_ids": entity_ids,
            "feature_names": feature_names
        }

        start_time = time.perf_counter()
        try:
            response = requests.post(f"{BASE_URL}/features/online", json=data)
            end_time = time.perf_counter()

            if response.status_code == 200:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        except Exception as e:
            print(f"  ✗ Error in request {i}: {e}")

    return latencies


def print_statistics(latencies: List[float], test_name: str):
    """Print latency statistics"""
    if not latencies:
        print(f"\n{test_name}: No successful requests")
        return

    sorted_latencies = sorted(latencies)

    print(f"\n{'='*60}")
    print(f"{test_name} Results")
    print(f"{'='*60}")
    print(f"Total Requests:    {len(latencies)}")
    print(f"Min Latency:       {min(latencies):.2f} ms")
    print(f"Max Latency:       {max(latencies):.2f} ms")
    print(f"Mean Latency:      {statistics.mean(latencies):.2f} ms")
    print(f"Median Latency:    {statistics.median(latencies):.2f} ms")
    print(f"P50 Latency:       {sorted_latencies[int(len(sorted_latencies) * 0.50)]:.2f} ms")
    print(f"P95 Latency:       {sorted_latencies[int(len(sorted_latencies) * 0.95)]:.2f} ms")
    print(f"P99 Latency:       {sorted_latencies[int(len(sorted_latencies) * 0.99)]:.2f} ms")
    print(f"Std Deviation:     {statistics.stdev(latencies):.2f} ms")

    # Check if under 10ms
    p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
    if p95_latency < 10:
        print(f"\n SUCCESS: P95 latency is under 10ms ({p95_latency:.2f} ms)")
    else:
        print(f"\n WARNING: P95 latency exceeds 10ms ({p95_latency:.2f} ms)")

    print(f"{'='*60}\n")


def main():
    print("="*60)
    print("Feature Store Performance Benchmark")
    print("="*60)

    try:
        # Step 1: Register features
        register_test_features()

        # Step 2: Ingest test data
        ingest_test_data(num_entities=1000)

        # Step 3: Benchmark single entity retrieval
        single_latencies = benchmark_single_entity_retrieval(num_requests=1000)
        print_statistics(single_latencies, "Single Entity Retrieval")

        # Step 4: Benchmark batch retrieval
        batch_latencies = benchmark_batch_retrieval(num_requests=100, batch_size=10)
        print_statistics(batch_latencies, "Batch Retrieval (10 entities)")

        # Step 5: Test with larger batch
        large_batch_latencies = benchmark_batch_retrieval(num_requests=100, batch_size=50)
        print_statistics(large_batch_latencies, "Batch Retrieval (50 entities)")

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\n\nBenchmark failed: {e}")


if __name__ == "__main__":
    main()
