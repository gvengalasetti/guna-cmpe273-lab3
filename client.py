from __future__ import annotations

import argparse
import random
import time

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover and call random service instance")
    parser.add_argument("--registry-url", default="http://127.0.0.1:8500")
    parser.add_argument("--service-name", default="demo-service")
    parser.add_argument("--calls", type=int, default=6)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    return parser.parse_args()


def discover_instances(registry_url: str, service_name: str) -> list[dict[str, str]]:
    response = requests.get(f"{registry_url}/services/{service_name}", timeout=3)
    response.raise_for_status()
    data = response.json()
    return data.get("instances", [])


def call_random_instance(instances: list[dict[str, str]]) -> dict:
    selected = random.choice(instances)
    url = f"http://{selected['host']}:{selected['port']}/hello"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    payload = response.json()
    payload["called_url"] = url
    return payload


def main() -> None:
    args = parse_args()
    called_instances: set[str] = set()

    for call_index in range(1, args.calls + 1):
        instances = discover_instances(args.registry_url, args.service_name)
        if not instances:
            print(f"call {call_index}: no instances found for {args.service_name}")
            time.sleep(args.delay_seconds)
            continue

        discovered = sorted(instance.get("instance_id", "unknown") for instance in instances)
        print(f"call {call_index}: discovered instances={discovered}")

        payload = call_random_instance(instances)
        called_instances.add(payload["instance_id"])
        print(
            f"call {call_index}: instance={payload['instance_id']} "
            f"url={payload['called_url']} message={payload['message']}"
        )
        time.sleep(args.delay_seconds)

    print(f"summary: called_instances={sorted(called_instances)} total_unique={len(called_instances)}")


if __name__ == "__main__":
    main()