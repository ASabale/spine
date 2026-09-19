#!/usr/bin/env bash
# Fresh-context serial loop (snarktank/ralph pattern). One local Qwen builder.
# Never start a second GPU builder. Do not push.
set -u

export PATH="/opt/homebrew/bin:${HOME}/.local/bin:${HOME}/.mtplx/bin:${PATH}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
cd "$ROOT"

PRD="$DIR/prd.json"
PROMPT="$DIR/prompt.md"
PROGRESS="$DIR/progress.txt"
ARCHIVE="$DIR/archive"
LAST_BRANCH="$DIR/.last-branch"
LOCK="$ROOT/.spine/ralph.lock"
LOG="$ROOT/.spine/ralph.log"
MAX="${RALPH_ITERS:-10}"
MODEL="${RALPH_MODEL:-mtplx/mtplx-qwen38-27b-optimized-speed}"
SKILLS="${RALPH_SKILLS:-tdd,codebase-design,diagnosing-bugs}"
OMP="${OMP:-$(command -v omp || true)}"
UV="${UV:-$(command -v uv || true)}"
PY="${PY:-$(command -v python3 || true)}"
# Short enough that a stuck local model yields the next fresh instance.
MAX_TIME="${RALPH_MAX_TIME:-8m}"
if [[ -z "$OMP" || -z "$UV" || -z "$PY" ]]; then
  echo "need omp, uv, and python3 on PATH" >&2
  exit 127
fi

prd_open() {
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(sum(1 for s in d["userStories"] if not s.get("passes")))' "$PRD"
}
prd_next() {
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); xs=sorted([s for s in d["userStories"] if not s.get("passes")], key=lambda s: s.get("priority", 99)); s=xs[0]; print(s["id"], s["title"])' "$PRD"
}
prd_branch() {
  "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("branchName") or "")' "$PRD"
}

mkdir -p "$ROOT/.spine"

if [[ -f "$LOCK" ]]; then
  old="$(cat "$LOCK" 2>/dev/null || true)"
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    echo "ralph already running pid=$old" >&2
    exit 1
  fi
fi
echo "$$" >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

log() { printf '%s %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$LOG"; }

if [[ ! -f "$PRD" ]]; then
  log "missing $PRD"
  exit 1
fi
if [[ ! -x "$PY" ]]; then
  log "python3 required at $PY"
  exit 1
fi

if [[ -f "$LAST_BRANCH" ]]; then
  current="$(prd_branch)"
  last="$(cat "$LAST_BRANCH" 2>/dev/null || true)"
  if [[ -n "$current" && -n "$last" && "$current" != "$last" ]]; then
    folder="$(echo "$last" | sed 's|^ralph/||')"
    dest="$ARCHIVE/$(date +%Y-%m-%d)-$folder"
    mkdir -p "$dest"
    cp "$PRD" "$dest/" 2>/dev/null || true
    [[ -f "$PROGRESS" ]] && cp "$PROGRESS" "$dest/"
    log "archived $last -> $dest"
    printf '# Ralph Progress Log\nStarted: %s\n---\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$PROGRESS"
  fi
fi
prd_branch >"$LAST_BRANCH"

if [[ ! -f "$PROGRESS" ]]; then
  printf '# Ralph Progress Log\nStarted: %s\n---\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >"$PROGRESS"
fi

open="$(prd_open)"
if [[ "$open" -eq 0 ]]; then
  log "prd complete (0 open stories)"
  exit 0
fi

log "ralph start max=$MAX open=$open model=$MODEL max_time=$MAX_TIME"

for i in $(seq 1 "$MAX"); do
  open="$(prd_open)"
  if [[ "$open" -eq 0 ]]; then
    log "iter=$i prd complete"
    exit 0
  fi
  next="$(prd_next)"
  log "iter=$i/$MAX story=$next"

  # Feed ONLY prompt.md (agent reads prd.json + progress.txt). Do not @ dump.
  # || true: a deadline must not kill the loop (snarktank uses the same).
  set +e
  BUILDER="$HOME/.omp/agent/agents/builder.md"
  OUTPUT="$(cat "$PROMPT" | "$OMP" -p \
    --cwd "$ROOT" \
    --auto-approve \
    --approval-mode yolo \
    --no-session \
    --max-time "$MAX_TIME" \
    --model "$MODEL" \
    --skills "$SKILLS" \
    --append-system-prompt "$BUILDER" \
    2>&1 | tee -a "$LOG")"
  rc="${PIPESTATUS[0]}"
  log "iter=$i builder exit=$rc"

  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    log "COMPLETE at iter=$i"
    exit 0
  fi

  if "$UV" run pytest -q; then
    log "iter=$i pytest green"
  else
    log "iter=$i pytest red"
  fi
  sleep 2
done

log "hit max=$MAX"
exit 1
