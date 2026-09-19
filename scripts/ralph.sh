#!/usr/bin/env bash
# Trampoline: implementation lives in scripts/ralph/ (snarktank layout).
exec bash "$(cd "$(dirname "$0")" && pwd)/ralph/ralph.sh" "$@"
