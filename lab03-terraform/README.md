# Lab 03: Terraform + Containerlab (Infrastructure as Code)

## Objective
Deploy a Containerlab network topology using Terraform's declarative IaC model.
Demonstrate the plan/apply/destroy lifecycle and state management.

## Stack
- IaC: Terraform (null_resource + local-exec)
- Environment: Containerlab + Nokia SR Linux
- Validation: Nornir (from Lab 02)

## Why Terraform for Network Automation?
- Declarative: define desired state, not steps.
- State: Terraform tracks what it created, enabling safe destroy/modify.
- Plan: preview changes before applying.

## Run It

### 1. Deploy
    terraform init
    terraform plan
    terraform apply -auto-approve

### 2. Validate (wait 3-4 minutes for SR Linux to boot)
    python3 backup_and_validate.py

### 3. Destroy
    terraform destroy -auto-approve

## Key Takeaway
Terraform brings the cloud IaC mindset to network labs. Even without a native
Containerlab provider, local-exec provisioners let you orchestrate tools
declaratively with full state tracking.
