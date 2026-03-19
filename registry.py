from __future__ import annotations

import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request


app = Flask(__name__)
_lock = threading.Lock()
_services: dict[str, dict[str, dict[str, str]]] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.post("/register")
def register_service():
    payload = request.get_json(silent=True) or {}
    service_name = str(payload.get("service_name", "")).strip()
    instance_id = str(payload.get("instance_id", "")).strip()
    host = str(payload.get("host", "")).strip()
    port = payload.get("port")

    if not service_name or not instance_id or not host or not isinstance(port, int):
        return jsonify({"error": "service_name, instance_id, host and int port are required"}), 400

    entry = {
        "instance_id": instance_id,
        "host": host,
        "port": str(port),
        "registered_at": _utc_now(),
    }

    with _lock:
        _services.setdefault(service_name, {})[instance_id] = entry

    return jsonify({"status": "registered", "service": service_name, "instance": entry}), 201


@app.get("/services/<service_name>")
def discover_service(service_name: str):
    with _lock:
        instances = list(_services.get(service_name, {}).values())
    return jsonify({"service_name": service_name, "instances": instances})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8500, debug=False)