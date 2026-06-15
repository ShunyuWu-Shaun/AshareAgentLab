#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-172.23.181.67}"
REMOTE_USER="${REMOTE_USER:-xxw}"
REMOTE_DIR="${REMOTE_DIR:-~/AshareAgentLab}"
REPO_URL="${REPO_URL:-https://github.com/ShunyuWu-Shaun/AshareAgentLab.git}"

ssh "${REMOTE_USER}@${REMOTE_HOST}" "if [ -d ${REMOTE_DIR}/.git ]; then cd ${REMOTE_DIR} && git pull --ff-only; else git clone ${REPO_URL} ${REMOTE_DIR}; fi"

