#!/usr/bin/env bash
#
# gateway_sync.sh - regenerate the per-domain Certificates and the Gateway
# listeners from domains.txt and apply them to the current kubectl context.
# Add a domain to domains.txt and re-run; that is the whole workflow.
#
# This only manages the periodic resources (certificates + gateway). The
# one-time bootstrap (namespace, Cloudflare Secret, ACME Issuer) lives in
# issuer.py and is applied separately, so this script needs no credentials.
#
# Run manually on a host that already has a working kubectl context.
#
# Usage:
#   ./gateway_sync.sh             # generate + kubectl apply
#   ./gateway_sync.sh --dry-run   # print the manifest, do not apply
#   DOMAINS_FILE=other.txt ./gateway_sync.sh   # use a different domain list

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAINS_FILE="${DOMAINS_FILE:-$SCRIPT_DIR/domains.txt}"

if [[ ! -f "$DOMAINS_FILE" ]]; then
  echo "domain list not found: $DOMAINS_FILE" >&2
  exit 1
fi

manifest="$(python3 "$SCRIPT_DIR/gateway.py" \
  --resources certificates,gateway \
  --domains_file "$DOMAINS_FILE")"

if [[ "${1:-}" == "--dry-run" ]]; then
  printf '%s\n' "$manifest"
  exit 0
fi

printf '%s\n' "$manifest" | kubectl apply -f -
