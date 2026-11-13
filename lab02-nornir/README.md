# Lab 02: Nornir Config Backup + Validation (Nokia SR Linux)

## Objective
Use Nornir (Python) to back up running configs and validate a declarative
assertion across a 2-node SR Linux fabric in parallel.

Unlike Lab 01 (Ansible), this lab demonstrates programmatic orchestration:
custom filtering, structured data output, and hard assertions that fail the
script when state drifts.

## Stack
- Automation: Nornir 3.x + pygnmi (gNMI transport)
- Environment: Containerlab (WSL-Containerlab distribution)
- Devices: 2x Nokia SR Linux (ixr-d2l), gNMI on port 57401 (insecure)

## Why Nornir instead of Ansible here?
- Ansible excels at declarative config push (Lab 01).
- Nornir excels at **data collection, validation, and conditional logic**
  where YAML playbooks become unwieldy.
- The two are complementary. This lab uses Ansible to seed state and Nornir
  to verify it — a common real-world split.

## Prerequisites
    pip3 install --break-system-packages -r requirements.txt

## Run It

### 1. Deploy topology
    containerlab deploy -t topology.clab.yml

### 2. Confirm Nornir sees both devices
    python3 - <<'PY'
    from nornir import InitNornir
    nr = InitNornir(config_file="config.yaml")
    for n, h in nr.inventory.hosts.items():
        print(n, h.hostname)
    PY

### 3. Run backup + validation
    python3 backup_and_validate.py

### 4. Inspect backups
    ls -la backups/

## Expected Outcome
- Two timestamped JSON backups per device under `backups/` on every run.
- Validation passes only when `network-instance BLUE` exists on both devices.
- Script exits non-zero on any failure (CI-friendly).

## Execution Evidence

### Negative case — BLUE deleted, validation fails

Removed the network-instance via gNMI:

    python3 - <<'PY'
    from pygnmi.client import gNMIclient
    for host in ("172.20.20.2", "172.20.20.3"):
        with gNMIclient(target=(host, 57401),
                        username="admin", password="NokiaSrl1!",
                        insecure=True) as gc:
            gc.set(delete=["/network-instance[name=BLUE]"], datastore="running")
    PY

Then:

    $ python3 backup_and_validate.py
    ...
    vvvv validate_network_instance ** changed : False vvvv ERROR
    ValueError: srl1: network-instance 'BLUE' NOT found
    ...
    ValueError: srl2: network-instance 'BLUE' NOT found

### Positive case — BLUE re-added via Ansible, validation passes

    $ ansible-playbook -i /tmp/inv.ini /tmp/push_blue.yml
    ...
    changed: [srl1]
    changed: [srl2]

    $ python3 backup_and_validate.py
    ...
    srl1: network-instance 'BLUE' OK
    srl2: network-instance 'BLUE' OK

    All devices passed backup + validation.

### Backups accumulate per run (no overwrite)

    $ ls -la backups/
    -rw-r--r-- 1 clab clab 94171 Nov 14 02:02 srl1-20261113T230222Z.json
    -rw-r--r-- 1 clab clab 94005 Nov 14 02:01 srl1-20261113T230111Z.json
    -rw-r--r-- 1 clab clab 94005 Nov 14 01:56 srl1-20261113T225617Z.json
    ...
    -rw-r--r-- 1 clab clab 94171 Nov 14 02:02 srl2-20261113T230222Z.json

## Cleanup
    containerlab destroy -t topology.clab.yml

## Key Takeaway
Nornir gives you Python's full expressiveness for network state.
When you need `if/else`, structured output, or assertions, Nornir is the
right tool; when you need declarative config at scale, Ansible still wins.

## Security Note
The credentials in `inventory/defaults.yaml` (`admin` / `NokiaSrl1!`) are the
public default credentials for Nokia SR Linux lab images. They are not secrets
and are only valid inside the Containerlab sandbox.
