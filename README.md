# Lab 01: Ansible + Containerlab (Nokia SR Linux)

## Objective
Deploy a single-node SR Linux topology with Containerlab and use Ansible's
`nokia.srlinux.config` module to enforce declarative config state idempotently.

## Stack
- Automation: Ansible (`nokia.srlinux` collection)
- Environment: Containerlab (WSL-Containerlab distribution)
- Device: Nokia SR Linux (ixr-d2l)

## Run It

### 1. Deploy topology
    containerlab deploy -t topology.clab.yml

### 2. Verify reachability
    ansible -i inventory.ini srlinux -m ping

### 3. Dry run
    ansible-playbook -i inventory.ini playbooks/vlan_push.yml --check --diff

### 4. Apply
    ansible-playbook -i inventory.ini playbooks/vlan_push.yml

### 5. Verify on device
    ssh admin@172.20.20.2
    # password: NokiaSrl1!
    info network-instance BLUE

## Expected Outcome
- Network instance BLUE exists and is admin-enabled.
- Second run reports changed=false (idempotency proven).

## Cleanup
    containerlab destroy -t topology.clab.yml

## Key Takeaway
Model-driven config + declarative resource modules = minimal diff, safe re-runs.

## Execution Evidence

### First apply — changes made
    TASK [Create a network instance (VRF) named BLUE] ***
    changed: [srl1]

    TASK [Create interface ethernet-1/1 as a member of BLUE] ***
    changed: [srl1]

    PLAY RECAP ***
    srl1 : ok=3 changed=2 failed=0 skipped=0

### Second apply — idempotency proven
    PLAY RECAP ***
    srl1 : ok=2 changed=0 failed=0 skipped=1

### Device verification (SR Linux CLI)
    A:admin@srl1# info network-instance BLUE
        type ip-vrf
        admin-state enable

    A:admin@srl1# info interface ethernet-1/1
        admin-state enable
        subinterface 0 {
            admin-state enable
        }

## Security Note

The credentials in `inventory.ini` (`admin` / `NokiaSrl1!`) are the public default credentials for Nokia SR Linux lab images. They are not secrets and are only valid inside the Containerlab sandbox. For production, credentials should be injected via Ansible Vault or environment variables.
