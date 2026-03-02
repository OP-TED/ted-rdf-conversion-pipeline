# AWS Infrastructure — TED-RDF Conversion Pipeline

CloudFormation-based infrastructure-as-code for the TED Semantic Web Service (TED-SWS) running on AWS ECS Fargate.

> **Scope**: This is Meaningfy's internal deployment tool. The client (OP) follows a separate installation manual. CFN and the manual are independent — different names/approaches are expected.

## Environment

- **AWS Account**: *(see team credentials)*
- **Region**: `eu-west-1`
- **Profile**: *(see team credentials)*

## Architecture

The root CloudFormation stack orchestrates 4 nested stacks:

```
root-stack.yaml
├── storage.yaml         — 4 EFS volumes + 8 mount targets
├── data-services.yaml   — RDS (airflow + metabase), DocumentDB, ElastiCache Redis
├── platform.yaml        — ECS cluster, Cloud Map namespace, 7 log groups, S3 env-file bucket, 7 ECR repos, IAM roles
└── services.yaml        — 7 task definitions, 7 ECS services, 6 Cloud Map service registrations
```

**Pre-existing (not managed by CFN)**: VPC, subnets, and security groups are passed as stack parameters.

### Services

| Service | CPU | RAM | Count | Ports |
|---|---|---|---|---|
| airflow | 4 vCPU | 16 GB | 1 | 8080, 5555 |
| worker | 4 vCPU | 8 GB | 2 | 8793 |
| fuseki | 2 vCPU | 8 GB | 1 | 3030 |
| metabase | 2 vCPU | 8 GB | 1 | 3000 |
| digest-api | 2 vCPU | 4 GB | 1 | 8000 |
| mongo-express | 1 vCPU | 2 GB | 1 | 8081 |
| sftp | 0.5 vCPU | 1 GB | 1 | 22 |

These are sandbox-sized defaults. Production sizing follows the installation manual specs.

### Configuration

All container configuration is loaded from a single `.env` file stored in an S3 bucket, using ECS's native `EnvironmentFiles` mechanism.

- **S3 bucket**: `ted-sws-env-{env}-{account-id}` (encrypted, versioned, all public access blocked)
- **Loading**: Every container in every task definition uses `EnvironmentFiles` to pull the `.env` from S3 at launch
- **No inline env vars**: Task definitions are pure structure (containers, mounts, ports, dependencies). All config lives in the `.env`.
- **Workflow**: Fill `env.template` → upload via `scripts/upload-env.sh` → deploy/redeploy services

### Data Services

| Service | Engine | Sandbox Default | Key Config |
|---|---|---|---|
| `airflow-rds` | PostgreSQL 13 | `db.t3.medium` | 20 GB gp2, DB=airflow |
| `metabase-db` | PostgreSQL 13 | `db.t3.micro` | 20 GB gp2, DB=metabase |
| DocumentDB | 4.0.0 | `db.t3.medium` | TLS disabled, port 27017 |
| ElastiCache | Redis 6.2 | `cache.t3.small` | 1 node, port 6379 |

## Directory Structure

```
src/infra/aws/
├── README.md                    — This file
├── env.template                 — Complete config template (all manual variables)
├── cloudformation/              — CFN templates (the source of truth)
│   ├── root-stack.yaml          — Nested stack orchestrator
│   ├── storage.yaml             — 4 EFS volumes + mount targets
│   ├── data-services.yaml       — RDS, DocumentDB, ElastiCache
│   ├── platform.yaml            — Cluster, Cloud Map, logs, S3, ECR, IAM
│   └── services.yaml            — Task defs, ECS services, Cloud Map
└── scripts/                     — Operational scripts
    ├── upload-env.sh            — Upload .env to S3 (AES256 encrypted)
    └── create-and-deploy-images.sh — Build + push images to ECR (podman)
```

## Naming Convention

All CFN-managed resources follow `ted-sws-*-{env}` with `Environment` as a parameter (`sandbox` | `staging` | `production`):

| Resource Type | Pattern | Example |
|---|---|---|
| Root Stack | `ted-sws-{env}` | `ted-sws-sandbox` |
| ECS Cluster | `ted-sws-{env}` | `ted-sws-sandbox` |
| Cloud Map NS | `ted-sws-{env}.local` | `ted-sws-sandbox.local` |
| IAM Roles | `ted-sws-*-role-{env}` | `ted-sws-execution-role-sandbox` |
| Log Groups | `/ecs/ted-sws-{env}/{service}` | `/ecs/.../airflow` |
| EFS Volumes | `ted-sws-{purpose}-{env}` | `...-airflow-logs-sandbox` |
| Task Families | `{component}-task-{env}` | `airflow-task-sandbox` |
| ECS Services | `{component}-service-{env}` | `airflow-service-sandbox` |
| S3 Env Bucket | `ted-sws-env-{env}-{account-id}` | `ted-sws-env-sandbox-<account-id>` |
| Cloud Map Svc | `{component}` (namespace-scoped) | `airflow` |
| ECR Repos | `ted-sws-{env}/{component}` | `.../sandbox/airflow` |

## Deployment Prerequisites

Before deploying the CFN stack:

1. **S3 bucket** for CFN templates (e.g. `ted-sws-cfn-templates`)
2. **Upload templates** to S3
3. **Deploy the stack**: `aws cloudformation create-stack ...` (creates all resources including S3 env bucket and ECR repos)
4. **Build and push images to ECR**: run `scripts/create-and-deploy-images.sh`
5. **Fill in `.env`** from `env.template` with actual credentials and endpoints (use RDS/DocumentDB/Redis endpoints from stack outputs)
6. **Upload `.env` to S3**: run `scripts/upload-env.sh`
7. **Force new deployment** on all services to pick up the `.env` and images

> **Note**: Services will fail to start until steps 4-6 are complete — ECS needs both the images in ECR and the `.env` in S3. This is expected. ECS retries automatically with backoff, and services will self-heal once images are pushed, the `.env` is uploaded, and a new deployment is forced.

### Networking Parameters (from existing VPC)

These are pre-provisioned by the client and not managed by CFN. Obtain the actual values from the team or the AWS Console before deploying.

| Parameter | Description |
|---|---|
| VpcId | Pre-existing VPC |
| SubnetId1 | First private subnet |
| SubnetId2 | Second private subnet |
| SecurityGroupId | Shared security group for ECS + EFS |

## Key Design Decisions

1. **S3 `EnvironmentFiles` for all configuration** — Every container loads a single `.env` from S3 at launch. No SSM Parameter Store, no inline `Environment:` key/value pairs. Task definitions are pure structure.

2. **Container-based SFTP** — Uses `atmoz/sftp:debian` on ECS.

3. **Dedicated IAM roles** — Execution role and task role are CFN-managed with full lifecycle ownership. Execution role includes S3 env-file access, CloudWatch Logs, and ECR pull. Task role includes ECS Exec (SSM) permissions.

4. **EFS always created new** — No import/reuse parameters needed. DeletionPolicy: Retain.

5. **`ec-scheduler` tag** — RDS instances should have `ec-scheduler: ec-office-hours-rds` for auto-stop.

6. **data-services.yaml defaults are sandbox-sized** — Production follows the installation manual specs.

7. **ECS Exec enabled on all services** — `EnableExecuteCommand: true` for interactive debugging via `aws ecs execute-command`.

## Teardown

To tear down the entire stack, delete the root CFN stack:

```bash
aws cloudformation delete-stack --stack-name ted-sws-<env> --profile <your-profile> --region eu-west-1
```

This deletes all nested stacks and their resources. ECR repositories have `DeletionPolicy: Retain` and survive stack deletion — delete them manually if needed:

```bash
aws ecr delete-repository --repository-name ted-sws-<env>/<component> --force
```

**Not managed by CFN** (delete manually if needed): VPC, subnets, security groups.
