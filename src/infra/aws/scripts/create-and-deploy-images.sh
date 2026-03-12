#!/usr/bin/env bash
# ==============================================================================
# Create ECR Repositories and Push Container Images
# ==============================================================================
# Creates ECR repositories under the environment-specific namespace and pushes
# Docker Hub / custom-built images to them.
#
# Usage:
#   ./create-and-deploy-images.sh [--env sandbox|staging|production] [--profile PROFILE] [--region REGION]
#
# Prerequisites:
#   - AWS CLI v2 configured with appropriate credentials
#   - Podman installed (used instead of Docker)
#   - A .env file in the same directory (for AWS_ACCOUNT_ID and build context)
#   - Source code checked out at ../../ (for building airflow + digest-api images)
#
# ECR Naming:
#   ted-sws-{env}/{component}
#   e.g. ted-sws-sandbox/airflow
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Defaults ----------------------------------------------------------------
ENVIRONMENT="sandbox"
PROFILE=""
REGION="eu-west-1"
ENV_FILE="${AWS_DIR}/.env"

# --- Docker Hub source images ------------------------------------------------
BUSYBOX_IMAGE="docker.io/busybox:1.36.1"
FUSEKI_IMAGE="docker.io/secoresearch/fuseki:5.3.0"
METABASE_IMAGE="docker.io/metabase/metabase:v0.53.6.6"
MONGO_EXPRESS_IMAGE="docker.io/mongo-express:0.54.0"
SFTP_IMAGE="docker.io/atmoz/sftp:debian"

# --- Image lists --------------------------------------------------------------
IMAGES_TO_BUILD=(airflow digest-api)
IMAGES_FROM_DOCKER_HUB=(busybox fuseki metabase mongo-express sftp)
ALL_IMAGES=("${IMAGES_FROM_DOCKER_HUB[@]}" "${IMAGES_TO_BUILD[@]}")

# --- Parse arguments ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)       ENVIRONMENT="$2"; shift 2 ;;
    --profile)   PROFILE="$2";     shift 2 ;;
    --region)    REGION="$2";      shift 2 ;;
    --env-file)  ENV_FILE="$2";    shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--env sandbox|staging|production] [--profile PROFILE] [--region REGION]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- Validate ----------------------------------------------------------------
if [[ "$ENVIRONMENT" != "sandbox" && "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
  echo "ERROR: Invalid environment '$ENVIRONMENT'. Must be sandbox, staging, or production."
  exit 1
fi

# --- Load .env for AWS_ACCOUNT_ID --------------------------------------------
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${AWS_ACCOUNT_ID:-}" ]]; then
  echo "ERROR: AWS_ACCOUNT_ID not set. Set it in .env or export it."
  exit 1
fi

# --- Derived ------------------------------------------------------------------
ECR_PREFIX="ted-sws-${ENVIRONMENT}"
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

AWS_OPTS=(--region "$REGION")
if [[ -n "$PROFILE" ]]; then
  AWS_OPTS+=(--profile "$PROFILE")
fi

# --- Map component name → Docker Hub source image ----------------------------
docker_hub_image_for() {
  local component="$1"
  case "$component" in
    busybox)       echo "$BUSYBOX_IMAGE" ;;
    fuseki)        echo "$FUSEKI_IMAGE" ;;
    metabase)      echo "$METABASE_IMAGE" ;;
    mongo-express) echo "$MONGO_EXPRESS_IMAGE" ;;
    sftp)          echo "$SFTP_IMAGE" ;;
    *) echo ""; return 1 ;;
  esac
}

# --- Map component name → local build directory (relative to project root) ----
build_dir_for() {
  local component="$1"
  case "$component" in
    airflow)    echo "src/infra/airflow" ;;
    digest-api) echo "src/infra/digest_api" ;;
    *) echo ""; return 1 ;;
  esac
}

# --- Map component name → versioned tag (empty = :latest only) ----------------
versioned_tag_for() {
  local component="$1"
  case "$component" in
    airflow)    echo "2.10.5-python3.10" ;;
    *)          echo "" ;;
  esac
}

# ==============================================================================
echo "============================================================"
echo "ECR Repository Setup"
echo "Environment: ${ENVIRONMENT}"
echo "Registry:    ${REGISTRY}"
echo "Prefix:      ${ECR_PREFIX}"
echo "Region:      ${REGION}"
echo "Profile:     ${PROFILE:-<default>}"
echo "============================================================"
echo ""

# --- Authenticate with ECR ---------------------------------------------------
echo "--- Authenticating with ECR ---"
aws ecr get-login-password "${AWS_OPTS[@]}" | \
  podman login --username AWS --password-stdin "${REGISTRY}"
echo ""

# --- Verify ECR repositories exist (created by CFN platform stack) -----------
echo "--- Verifying ECR Repositories ---"
for COMPONENT in "${ALL_IMAGES[@]}"; do
  REPO_NAME="${ECR_PREFIX}/${COMPONENT}"
  echo -n "  ${REPO_NAME} ... "
  if aws ecr describe-repositories "${AWS_OPTS[@]}" \
       --repository-names "$REPO_NAME" > /dev/null 2>&1; then
    echo "ok"
  else
    echo "NOT FOUND — creating (expected to be created by CFN stack)"
    aws ecr create-repository "${AWS_OPTS[@]}" \
      --repository-name "$REPO_NAME" \
      --image-scanning-configuration scanOnPush=true > /dev/null
    echo "  created"
  fi
done
echo ""

# --- Pull & push Docker Hub images -------------------------------------------
echo "--- Pushing Docker Hub Images ---"
for COMPONENT in "${IMAGES_FROM_DOCKER_HUB[@]}"; do
  REPO_NAME="${ECR_PREFIX}/${COMPONENT}"
  ECR_URI="${REGISTRY}/${REPO_NAME}"
  SOURCE_IMAGE=$(docker_hub_image_for "$COMPONENT")
  # Extract the tag from the source image (e.g. "1.36.1", "5.3.0", "debian")
  SOURCE_TAG="${SOURCE_IMAGE##*:}"

  echo "  ${COMPONENT}: pulling ${SOURCE_IMAGE}"
  podman pull "$SOURCE_IMAGE"

  echo "  ${COMPONENT}: tagging → ${ECR_URI}:${SOURCE_TAG} + :latest"
  podman tag "$SOURCE_IMAGE" "${ECR_URI}:${SOURCE_TAG}"
  podman tag "$SOURCE_IMAGE" "${ECR_URI}:latest"

  echo "  ${COMPONENT}: pushing"
  podman push "${ECR_URI}:${SOURCE_TAG}"
  podman push "${ECR_URI}:latest"

  echo "  ${COMPONENT}: done"
  echo ""
done

# --- Build & push custom images -----------------------------------------------
echo "--- Building and Pushing Custom Images ---"
PROJECT_ROOT="${SCRIPT_DIR}/../../../.."

# Prepare build context (copy requirements etc.)
echo "  Preparing build context..."
cp "${PROJECT_ROOT}/requirements.txt" "${PROJECT_ROOT}/src/infra/airflow/"
cp "${PROJECT_ROOT}/requirements.txt" "${PROJECT_ROOT}/src/infra/digest_api/digest_service/project_requirements.txt"
cp -r "${PROJECT_ROOT}/src/ted_sws" "${PROJECT_ROOT}/src/infra/digest_api/"
(cd "${PROJECT_ROOT}" && make create-env-digest-api 2>/dev/null || true)

for COMPONENT in "${IMAGES_TO_BUILD[@]}"; do
  REPO_NAME="${ECR_PREFIX}/${COMPONENT}"
  ECR_URI="${REGISTRY}/${REPO_NAME}"
  BUILD_DIR=$(build_dir_for "$COMPONENT")
  FULL_BUILD_DIR="${PROJECT_ROOT}/${BUILD_DIR}"
  VERSIONED_TAG=$(versioned_tag_for "$COMPONENT")

  echo "  ${COMPONENT}: building from ${BUILD_DIR}/"
  podman build -t "${COMPONENT}" "${FULL_BUILD_DIR}" --label="${COMPONENT}-image"

  echo "  ${COMPONENT}: tagging → ${ECR_URI}:latest"
  podman tag "${COMPONENT}" "${ECR_URI}:latest"

  if [[ -n "$VERSIONED_TAG" ]]; then
    echo "  ${COMPONENT}: tagging → ${ECR_URI}:${VERSIONED_TAG}"
    podman tag "${COMPONENT}" "${ECR_URI}:${VERSIONED_TAG}"
  fi

  echo "  ${COMPONENT}: pushing"
  podman push "${ECR_URI}:latest"

  if [[ -n "$VERSIONED_TAG" ]]; then
    podman push "${ECR_URI}:${VERSIONED_TAG}"
  fi

  echo "  ${COMPONENT}: done"
  echo ""
done

# --- Write image URIs to .env (idempotent) ------------------------------------
echo "--- Writing Image URIs to .env ---"

# Remove any previous auto-generated ECR block so we don't create duplicates
ECR_MARKER="# --- ECR Image URIs"
if grep -q "$ECR_MARKER" "$ENV_FILE"; then
  # Delete from the first ECR marker line to end of file, then re-add a newline
  sed -i "/${ECR_MARKER}/,\$d" "$ENV_FILE"
fi

{
  echo "# --- ECR Image URIs ----------------------------------------------------------"
  echo "AIRFLOW_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/airflow:latest"
  echo "FUSEKI_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/fuseki:latest"
  echo "METABASE_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/metabase:latest"
  echo "MONGO_EXPRESS_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/mongo-express:latest"
  echo "DIGEST_API_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/digest-api:latest"
  echo "SFTP_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/sftp:latest"
  echo "BUSYBOX_IMAGE_URI=${REGISTRY}/${ECR_PREFIX}/busybox:latest"
} >> "$ENV_FILE"

echo "  Image URIs written to ${ENV_FILE}"
echo ""

# --- Cleanup ------------------------------------------------------------------
echo "--- Cleaning up local images ---"
podman system prune --all --force 2>/dev/null || true
podman rmi --all 2>/dev/null || true

echo ""
echo "============================================================"
echo "Done. ECR repositories and images ready."
echo ""
echo "Repository URIs:"
for COMPONENT in "${ALL_IMAGES[@]}"; do
  echo "  ${REGISTRY}/${ECR_PREFIX}/${COMPONENT}:latest"
done
echo "============================================================"
