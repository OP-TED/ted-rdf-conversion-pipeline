#!/usr/bin/env bash
# ==============================================================================
# Upload .env file to S3 for ECS EnvironmentFiles
# ==============================================================================
# Uploads the .env file to the S3 bucket created by the platform stack.
# ECS task definitions reference this file via the EnvironmentFiles property,
# matching the installation manual's "Load the .env file into the container".
#
# Usage:
#   ./upload-env.sh --bucket BUCKET_NAME [--env-file FILE] [--profile PROFILE] [--region REGION]
#
# Prerequisites:
#   - AWS CLI v2 configured with appropriate credentials
#   - A .env file in the same directory (copy from env.template and fill in)
#   - The S3 bucket already created (by the CloudFormation platform stack)
#
# The script is idempotent — re-running overwrites the file in S3.
# The bucket has versioning enabled, so previous versions are preserved.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Defaults ----------------------------------------------------------------
BUCKET=""
PROFILE=""
REGION="eu-west-1"
ENV_FILE="${AWS_DIR}/.env"
DRY_RUN=false

# --- Parse arguments ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --bucket)    BUCKET="$2";     shift 2 ;;
    --profile)   PROFILE="$2";    shift 2 ;;
    --region)    REGION="$2";     shift 2 ;;
    --env-file)  ENV_FILE="$2";   shift 2 ;;
    --dry-run)   DRY_RUN=true;    shift   ;;
    -h|--help)
      echo "Usage: $0 --bucket BUCKET_NAME [--env-file FILE] [--profile PROFILE] [--region REGION] [--dry-run]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- Validate ----------------------------------------------------------------
if [[ -z "$BUCKET" ]]; then
  echo "ERROR: --bucket is required."
  echo "Get the bucket name from CloudFormation outputs:"
  echo "  aws cloudformation describe-stacks --stack-name <root-stack> --query 'Stacks[0].Outputs[?OutputKey==\`EnvFileBucketName\`].OutputValue' --output text"
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env file not found at $ENV_FILE"
  echo "Copy env.template to .env and fill in all values first."
  exit 1
fi

# --- Validate .env file is not empty -----------------------------------------
line_count=$(grep -c -v '^\s*$\|^\s*#' "$ENV_FILE" || true)
if [[ "$line_count" -eq 0 ]]; then
  echo "ERROR: .env file has no variable definitions (only comments/blanks)."
  exit 1
fi

# --- AWS CLI options ---------------------------------------------------------
AWS_OPTS=(--region "$REGION")
if [[ -n "$PROFILE" ]]; then
  AWS_OPTS+=(--profile "$PROFILE")
fi

# --- Upload ------------------------------------------------------------------
S3_KEY=".env"
S3_URI="s3://${BUCKET}/${S3_KEY}"

echo "============================================================"
echo "Uploading environment file to S3"
echo "Source:  ${ENV_FILE}"
echo "Target:  ${S3_URI}"
echo "Region:  ${REGION}"
echo "Profile: ${PROFILE:-<default>}"
echo "Dry run: ${DRY_RUN}"
echo "Variables: ${line_count} non-comment lines"
echo "============================================================"
echo ""

if [[ "$DRY_RUN" == true ]]; then
  echo "DRY RUN — would upload ${ENV_FILE} to ${S3_URI}"
  echo ""
  echo "Variables that would be uploaded:"
  grep -v '^\s*$\|^\s*#' "$ENV_FILE" | cut -d= -f1 | sort
  exit 0
fi

aws s3 cp "$ENV_FILE" "$S3_URI" \
  "${AWS_OPTS[@]}" \
  --sse AES256

echo ""
echo "============================================================"
echo "Done. File uploaded to ${S3_URI}"
echo ""
echo "To verify:"
echo "  aws s3 ls ${S3_URI} ${AWS_OPTS[*]}"
echo ""
echo "To view versions:"
echo "  aws s3api list-object-versions --bucket ${BUCKET} --prefix ${S3_KEY} ${AWS_OPTS[*]}"
echo ""
echo "After uploading, restart services to pick up the new .env:"
echo "  aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment"
echo "============================================================"
