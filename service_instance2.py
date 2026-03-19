from __future__ import annotations

import argparse
import time

import requests
from flask import Flask, jsonify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start one service instance")
    parser.add_argument("--service-name", default="demo-service")
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--registry-url", default="http://127.0.0.1:8500")
    parser.add_argument("--register-retries", type=int, default=20)
    return parser.parse_args()


def register_with_registry(args: argparse.Namespace) -> None:
    payload = {
        "service_name": args.service_name,
        "instance_id": args.instance_id,
        "host": args.host,
        "port": args.port,
    }

    for attempt in range(1, args.register_retries + 1):
        try:
            response = requests.post(f"{args.registry_url}/register", json=payload, timeout=2)
            response.raise_for_status()
            return
        except requests.RequestException:
            if attempt == args.register_retries:
                raise
            time.sleep(0.5)


def create_app(args: argparse.Namespace) -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "instance_id": args.instance_id})

    @app.get("/hello")
    def hello():
        return jsonify(
            {
                "message": "hello from service instance",
                "service_name": args.service_name,
                "instance_id": args.instance_id,
                "host": args.host,
                "port": args.port,
            }
        )

    return app


def main() -> None:
    args = parse_args()
    register_with_registry(args)
    app = create_app(args)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()