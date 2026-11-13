#!/usr/bin/env python3
"""
Lab 02: Nornir config backup + validation on Nokia SR Linux.
Uses pygnmi directly as the gNMI transport (port 57401, insecure).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from pygnmi.client import gNMIclient

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

GNMI_PORT = 57401


def _gnmi(task):
    """Build an insecure gNMI client for a given Nornir host."""
    return gNMIclient(
        target=(task.host.hostname, GNMI_PORT),
        username=task.host.username,
        password=task.host.password,
        insecure=True,
    )


def backup_config(task):
    """Retrieve full config tree via pygnmi and save to timestamped file."""
    with _gnmi(task) as gc:
        result = gc.get(path=["/"], datatype="config")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = BACKUP_DIR / f"{task.host.name}-{stamp}.json"
    with out.open("w") as f:
        json.dump(result, f, indent=2, default=str)
    return str(out)


def validate_network_instance(task, name: str = "BLUE"):
    """Assert that a given network-instance exists on the device."""
    path = f"/network-instance[name={name}]"
    with _gnmi(task) as gc:
        response = gc.get(path=[path], datatype="config")
    notifications = response.get("notification", []) if response else []
    for note in notifications:
        if note.get("update"):
            return f"{task.host.name}: network-instance '{name}' OK"
    raise ValueError(f"{task.host.name}: network-instance '{name}' NOT found")


def main() -> int:
    nr = InitNornir(config_file="config.yaml")
    srlinux = nr.filter(F(groups__contains="srlinux"))
    print(f"Targets: {list(srlinux.inventory.hosts.keys())}")

    print("\n--- Step 1: Backup running config ---")
    backup_results = srlinux.run(task=backup_config)
    print_result(backup_results)

    print("\n--- Step 2: Validate network-instance BLUE ---")
    validate_results = srlinux.run(task=validate_network_instance)
    print_result(validate_results)

    failed = backup_results.failed + validate_results.failed
    if failed:
        print(f"\n{failed} device(s) failed. See output above.")
        return 1

    print("\nAll devices passed backup + validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
