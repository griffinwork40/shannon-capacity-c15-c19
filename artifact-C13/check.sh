#!/bin/sh
# check.sh -- one-command check of
#     Theta(C13) >= 6.302927071589786
# in Lean 4 (Buys-Polak-Zuiddam framework), with an independent Python evaluator, and an exact
# integer comparison with the prior bound Theta(C13) >= 6.302927046770772 (M. Protti,
# github.com/matthewprotti/c11-shannon-capacity-lower-bound, tag v0.5.0, C13R8D522.lean).
#
#   sh check.sh [--install-elan] [--python-only] [--dir DIR]
#
#   --install-elan  if `lake` is not found, run the official elan installer with
#                   --no-modify-path (installs into ~/.elan; your shell profile is not edited)
#   --python-only   run steps 0-3b only (no Lean needed). Not a substitute for the Lean check.
#   --dir DIR       work directory (default ./c13-check); must not already contain
#                   shannon-capacity-lean/ or protti/ (this script never deletes anything)
#
# Steps:
#   0. fingerprint the bundle files (certC13.patch, eval_c13.py, compare_protti.py, schedule);
#   1. clone github.com/spectra-research/shannon-capacity-lean into DIR, check out aa21eeb;
#   2. apply certC13.patch; verify the four new files and that the only change to an existing
#      BPZ file is four added import lines in ShannonBounds.lean;
#   3. Python (stdlib only): eval_c13.py re-derives tables, codes and base sizes from BPZ's
#      Lean sources, must reproduce BPZ's own CertC13/C15/C19/C7 exactly (positive controls),
#      and must evaluate the schedule to the same M as the Lean literal CertC13b.M;
#   3b. clone Protti's repository at v0.5.0 and compare exactly: M^522 > N^522 for his literal N;
#   4. find lake; check Lean version;
#   5. lake exe cache get ; lake build ShannonBounds.CapCertC13b ;
#   6. fresh Lean process: re-type-check the statement verbatim, #print axioms, fail on
#      sorryAx or any axiom outside {propext, Classical.choice, Quot.sound, *.native_decide.ax_*};
#   7. grep all Lean sources for sorry/admit.
#
# Needs: git, curl (only for --install-elan), python3 (>= 3.8), sha256sum or shasum, awk,
# sed, grep, cmp; about 8 GB disk; network access to github.com and the Mathlib cache.
# Knobs: LEAN_NUM_THREADS (default 4), NICE (default 5).
# Writes only inside DIR, plus the usual elan/Mathlib caches (~/.elan, ~/.cache/mathlib).
set -eu

BPZ_URL="https://github.com/spectra-research/shannon-capacity-lean"
BPZ_SHA="aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65"
PROTTI_URL="https://github.com/matthewprotti/c11-shannon-capacity-lower-bound"
PROTTI_TAG="v0.5.0"
PROTTI_SHA="dfaef37e60e55c55b1744d9badd1f26c5364c7d5"
BUNDLE_SHA256="
certC13.patch:7fde38bcb178fb747be18bb9deb63f303225c2cc0b7e1d566281ad47fb301138
eval_c13.py:4de5d55a0ea0005c932fb9aa1bfab3bde3059bd9143c9fc3db75f934ba4de4ec
compare_protti.py:790710c268b7b5f442d192d8d863cfd039cdf00b3066e2332826713d17c18381
schedules/best_C13_SA1.json:0843977febf93c1be1932e43a7e3cb34f382ec3b672f85e8ac9847d91eba7407
"
FILES_SHA256="
ShannonBounds/DagTail.lean:f277d0b7695904f6339f760e6c37a51b40654d2b546e61d657bf268153efe147
ShannonBounds/DagCode3.lean:fa3f760ff74d11f870728d1f5b5a2bb37de149ab9525d7986f6d131e60763377
ShannonBounds/CertC13b.lean:cffbb8ab757a7f8d2d7b4b8cfa6d3597431e77b725f39f87d6a9768946e22564
ShannonBounds/CapCertC13b.lean:5c5558263bf78fde7d54d191eb0e58611ad38997a334b4959dacfa97dd77ea6a
"
# sha256 of the decimal digits of M (no newline); equal to the Lean literal CertC13b.M
M13_SHA256="cac3a5bdf4a4f34045c3a80c52bb1d651e5a0ff2a007b3f13efb6a9ab0914fba"
DEC13="6.302927071589786"; BPZ13="6.302926729310108"; PROTTI13="6.302927046770772"
THM13="ShannonBounds.CapCertC13b.shannonCapacity_cycleGraph_13_ge"
NEW_IMPORTS="import ShannonBounds.DagTail
import ShannonBounds.DagCode3
import ShannonBounds.CertC13b
import ShannonBounds.CapCertC13b"

HERE=$(cd "$(dirname "$0")" && pwd)
DIR="$(pwd)/c13-check"
INSTALL_ELAN=0
PYTHON_ONLY=0

usage() { sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --install-elan) INSTALL_ELAN=1 ;;
    --python-only) PYTHON_ONLY=1 ;;
    --dir) [ $# -ge 2 ] || { echo "--dir needs an argument" >&2; exit 2; }; DIR="$2"; shift ;;
    --dir=*) DIR="${1#--dir=}" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

: "${LEAN_NUM_THREADS:=4}"; export LEAN_NUM_THREADS
: "${NICE:=5}"

say()  { printf '\n==> %s\n' "$*"; }
fail() { printf '\nCHECK FAILED: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "required tool not found: $1"; }
sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  else fail "need sha256sum or shasum"; fi
}
lean_M() { awk '/^def M : Nat :=/{getline; gsub(/[ \t\r]/,""); printf "%s", $0; exit}' "$1"; }

say "check.sh started $(date -u '+%Y-%m-%dT%H:%M:%SZ') on $(uname -sm)"
echo "    bundle: $HERE"
echo "    work dir: $DIR    LEAN_NUM_THREADS=$LEAN_NUM_THREADS  nice=$NICE"
need git; need awk; need grep; need sed; need cmp; need python3
echo "    $(git --version); $(python3 --version 2>&1)"

# ---------------------------------------------------------------- 0. bundle fingerprint
say "0. bundle fingerprint"
for pair in $BUNDLE_SHA256; do
  f=${pair%%:*}; want=${pair#*:}
  [ -f "$HERE/$f" ] || fail "bundle file missing: $f"
  got=$(sha256 "$HERE/$f")
  [ "$got" = "$want" ] || fail "bundle file $f has SHA-256 $got, expected $want"
  echo "    $f  $got  OK"
done
PATCH="$HERE/certC13.patch"

# ---------------------------------------------------------------- 1. clone + pin
BPZ="$DIR/shannon-capacity-lean"
PROT="$DIR/protti"
if [ -e "$BPZ" ] || [ -e "$PROT" ]; then fail "$BPZ or $PROT already exists; pass --dir to a fresh directory (this script never deletes anything)"; fi
mkdir -p "$DIR"
DIR=$(cd "$DIR" && pwd)
BPZ="$DIR/shannon-capacity-lean"; PROT="$DIR/protti"
say "1. cloning $BPZ_URL"
git clone "$BPZ_URL" "$BPZ"
cd "$BPZ"
git -c advice.detachedHead=false checkout "$BPZ_SHA"
HEAD_SHA=$(git rev-parse HEAD)
[ "$HEAD_SHA" = "$BPZ_SHA" ] || fail "HEAD is $HEAD_SHA, expected $BPZ_SHA"
echo "    HEAD = $HEAD_SHA ($(git log -1 --format='%ad %s' --date=iso))"
echo "    licence: $(head -n 2 LICENSE | tr -s ' ' | tr '\n' ' ')"
echo "    lean-toolchain: $(cat lean-toolchain)"
echo "    BPZ README row: $(grep -E '^\| 13 \|' README.md | tr '\n' ' ')"

# ---------------------------------------------------------------- 2. patch
say "2. applying certC13.patch"
git apply --check -v "$PATCH" || fail "patch does not apply cleanly to $BPZ_SHA"
git apply "$PATCH"
for pair in $FILES_SHA256; do
  f=${pair%%:*}; want=${pair#*:}
  [ -f "$f" ] || fail "$f was not created by the patch"
  got=$(sha256 "$f")
  [ "$got" = "$want" ] || fail "$f SHA-256 $got, expected $want"
  echo "    $f sha256 OK"
done
CHANGED=$(git diff --name-only)
[ "$CHANGED" = "ShannonBounds.lean" ] || fail "patch modified unexpected tracked files: $CHANGED"
if git diff -U0 ShannonBounds.lean | grep -E '^-[^-]' >/dev/null; then
  fail "patch removes lines from ShannonBounds.lean"
fi
ADDED=$(git diff -U0 ShannonBounds.lean | grep -E '^\+[^+]' | sed 's/^+//')
[ "$ADDED" = "$NEW_IMPORTS" ] || fail "ShannonBounds.lean: added lines are not exactly the four imports: $ADDED"
UNTRACKED=$(git ls-files --others --exclude-standard | sort | tr '\n' ' ')
[ "$UNTRACKED" = "ShannonBounds/CapCertC13b.lean ShannonBounds/CertC13b.lean ShannonBounds/DagCode3.lean ShannonBounds/DagTail.lean " ] \
  || fail "unexpected new files: $UNTRACKED"
echo "    only change to BPZ files: 4 import lines added to ShannonBounds.lean"
for f in $UNTRACKED; do
  if sed -e 's/--.*$//' "$f" | awk '/\/-/{c=1} !c{print} /-\//{c=0}' \
     | grep -nE '(^|[^A-Za-z0-9_.])(axiom|unsafe|opaque|implemented_by|extern|csimp|macro|macro_rules|syntax|elab|run_cmd|#eval|initialize|builtin_initialize)([^A-Za-z0-9_]|$)'; then
    fail "$f uses a forbidden keyword (listed above): only definitions/theorems are allowed"
  fi
done
echo "    added files declare no axioms and use no unsafe/opaque/implemented_by/extern/csimp/macros"
echo "    new files: $UNTRACKED"

# ---------------------------------------------------------------- 3. python
say "3. independent Python evaluator (stdlib only) on the fresh clone"
PY="$DIR/python"; mkdir -p "$PY"
cp "$HERE/eval_c13.py" "$PY/eval_c13.py"        # it writes M_C13.txt next to itself
PYLOG="$PY/eval_c13.log"
PYRUN='import sys, runpy
if not hasattr(sys, "set_int_max_str_digits"): sys.set_int_max_str_digits = lambda n: None
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")'
nice -n "$NICE" python3 -c "$PYRUN" "$PY/eval_c13.py" "$BPZ" \
  "$HERE/schedules/best_C13_SA1.json" \
  --lean "$BPZ/ShannonBounds/CertC13b.lean" > "$PYLOG" 2>&1 \
  || { cat "$PYLOG"; fail "eval_c13.py exited nonzero"; }
cat "$PYLOG"
pyreq() { grep -F -- "$1" "$PYLOG" >/dev/null || fail "python: $2"; }
pyreq "CONTROL CertC13: 26 nodes, all node literals match: True; M == Lean M: True; p=522 (README 522); digits=418 (README 418); root=$BPZ13 (README $BPZ13) -> PASS" \
  "positive control BPZ CertC13 ($BPZ13) not reproduced exactly"
pyreq "CONTROL CertC15: 23 nodes, all node literals match: True; M == Lean M: True; p=3664 (README 3664); digits=3164 (README 3164); root=7.301628695930103 (README 7.301628695930103) -> PASS" \
  "positive control BPZ CertC15 not reproduced exactly"
pyreq "CONTROL CertC19: 16 nodes, all node literals match: True; M == Lean M: True; p=11856 (README 11856); digits=11514 (README 11514); root=9.357200030000796 (README 9.357200030000796) -> PASS" \
  "positive control BPZ CertC19 not reproduced exactly"
pyreq "root trunc15 = $DEC13 ; a^p <= M*10^(15p): True ; (a+1)^p > M*10^(15p): True" "C13 root is not $DEC13"
pyreq "Lean M == my M (digit for digit): True" "Lean M != Python M"
pyreq "structural problems (S/children/exponents/tail args vs Rn defs): none" "structural mismatch with Lean"
pyreq "matches mine: True" "CapCert decimal/exponents mismatch"
[ -f "$PY/M_C13.txt" ] || fail "python did not write M_C13.txt"
tr -d '\n' < "$PY/M_C13.txt" > "$PY/M_C13.digits"
lean_M "ShannonBounds/CertC13b.lean" > "$PY/M_lean_CertC13b.digits"
cmp -s "$PY/M_C13.digits" "$PY/M_lean_CertC13b.digits" || fail "Python M differs from Lean literal CertC13b.M"
got=$(sha256 "$PY/M_C13.digits")
[ "$got" = "$M13_SHA256" ] || fail "sha256 of M is $got, expected $M13_SHA256"
echo "    C13: Python M == Lean CertC13b.M digit for digit ($(wc -c < "$PY/M_C13.digits" | tr -d ' ') digits, sha256 $got)"

# ---------------------------------------------------------------- 3b. prior bound, exact
say "3b. exact comparison with the prior bound (Protti $PROTTI_TAG)"
git clone -q "$PROTTI_URL" "$PROT"
( cd "$PROT" && git -c advice.detachedHead=false checkout -q "$PROTTI_TAG" && \
  [ "$(git rev-parse HEAD)" = "$PROTTI_SHA" ] ) || fail "Protti $PROTTI_TAG is not commit $PROTTI_SHA"
echo "    Protti $PROTTI_TAG = $PROTTI_SHA; HEAD of default branch: $(cd "$PROT" && git rev-parse origin/HEAD 2>/dev/null || echo '?')"
echo "    Protti tags: $(cd "$PROT" && git tag | tr '\n' ' ')"
python3 -c "$PYRUN" "$HERE/compare_protti.py" "$PY/M_C13.digits" \
  "$PROT/shannon_checked_release/source/ShannonBounds/C13R8D522.lean" 522 \
  || fail "our M does not exceed Protti's N exactly"
echo "    Python check OK"

if [ "$PYTHON_ONLY" = 1 ]; then
  say "PYTHON-ONLY CHECKS PASSED (steps 0-3b; Lean steps 4-7 skipped by --python-only)"
  echo "  The Lean build is the proof; rerun without --python-only to check it."
  exit 0
fi

# ---------------------------------------------------------------- 4. toolchain
say "4. locating lake"
EH="${ELAN_HOME:-$HOME/.elan}"
LAKE=""
if command -v lake >/dev/null 2>&1; then
  LAKE=$(command -v lake)
elif [ -x "$EH/bin/lake" ]; then
  LAKE="$EH/bin/lake"
  echo "    lake is not on PATH; using $LAKE (your PATH is not modified)."
elif [ "$INSTALL_ELAN" = 1 ]; then
  need curl
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$DIR/elan-init.sh"
  sh "$DIR/elan-init.sh" -y --no-modify-path --default-toolchain none
  LAKE="$EH/bin/lake"
  [ -x "$LAKE" ] || fail "elan install did not produce $LAKE"
else
  echo "lake not found; re-run with --install-elan. Python checks passed; Lean did not run." >&2
  exit 3
fi
LAKE_V=$("$LAKE" --version)
echo "    $LAKE_V"
WANT_V=$(sed 's/.*:v//' lean-toolchain)
case "$LAKE_V" in
  *"Lean version $WANT_V"*) echo "    Lean version matches lean-toolchain ($WANT_V)" ;;
  *) fail "lake reports a Lean version other than $WANT_V (lean-toolchain). Use elan's lake." ;;
esac

# ---------------------------------------------------------------- 5. build
say "5a. lake exe cache get (prebuilt Mathlib)"
nice -n "$NICE" "$LAKE" exe cache get
MATHLIB_REV=$(python3 -c 'import json,sys; print([p["rev"] for p in json.load(open(sys.argv[1]))["packages"] if p["name"]=="mathlib"][0])' lake-manifest.json) \
  || fail "cannot read the Mathlib revision from lake-manifest.json"
echo "    Mathlib revision (lake-manifest.json): $MATHLIB_REV"
say "5b. lake build ShannonBounds.CapCertC13b"
T0=$(date +%s)
nice -n "$NICE" "$LAKE" build ShannonBounds.CapCertC13b
echo "    build OK in $(( $(date +%s) - T0 )) s"

# ---------------------------------------------------------------- 6. statements + axioms
say "6. theorem statement and axioms (fresh Lean process on the built modules)"
PROBE="$DIR/probe_axioms.lean"
cat > "$PROBE" <<EOM
import ShannonBounds.CapCertC13b
open SimpleGraph
#check @$THM13
example : ($DEC13 : ℝ) ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 13) :=
  $THM13
example : ($PROTTI13 : ℝ) < $DEC13 := ShannonBounds.CapCertC13b.improves_1
#print ShannonBounds.shannonCapacity
#print axioms $THM13
EOM
OUT="$DIR/probe_axioms.out"
nice -n "$NICE" "$LAKE" env lean "$PROBE" > "$OUT" 2>&1 || { cat "$OUT"; fail "lean probe failed"; }
cat "$OUT"
if grep -E '(^|:)[0-9]+:[0-9]+: error' "$OUT" >/dev/null; then fail "lean probe reported an error"; fi
FLAT=$(tr '\n' ' ' < "$OUT" | tr -s ' ')
echo "$FLAT" | grep -F "shannonCapacity_cycleGraph_13_ge : $DEC13 ≤ ShannonBounds.shannonCapacity (cycleGraph 13)" >/dev/null \
  || fail "C13 theorem statement not as expected"
echo "    statement OK: ($DEC13 : ℝ) ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 13)"
NLIST=$(grep -c "depends on axioms" "$OUT" || true)
[ "$NLIST" = 1 ] || fail "#print axioms produced $NLIST axiom lists, expected 1"
if grep -F "sorryAx" "$OUT" >/dev/null; then fail "the theorem depends on sorryAx"; fi
BAD=$(sed -n '/depends on axioms/,$p' "$OUT" | tr -d '[],' | tr ' ' '\n' | sed 's/^ *//' \
      | grep -v -e '^$' -e "^'" -e '^depends$' -e '^on$' -e '^axioms:$' \
                -e '^propext$' -e '^Classical\.choice$' -e '^Quot\.sound$' \
                -e '\._native\.native_decide\.ax_[0-9_]*$' || true)
[ -z "$BAD" ] || fail "unexpected axioms: $BAD"
NAX=$(sed -n '/depends on axioms/,$p' "$OUT" | grep -o '_native\.native_decide\.ax_[0-9_]*' | wc -l | tr -d ' ')
echo "    axioms OK: propext, Classical.choice, Quot.sound + $NAX native_decide auxiliary axioms; no sorryAx"

# ---------------------------------------------------------------- 7. sorry grep
say "7. grep for sorry/admit in all Lean sources"
if grep -rnw --include='*.lean' -e sorry -e admit ShannonBounds ShannonBounds.lean; then
  fail "found sorry/admit in the Lean sources (listed above)"
fi
echo "    no sorry/admit in ShannonBounds/*.lean or ShannonBounds.lean"

say "summary: BPZ $BPZ_SHA + certC13.patch; $LAKE_V; Mathlib $MATHLIB_REV; finished $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "ALL CHECKS PASSED (Lean 4 build + statement + axioms, independent Python with exact BPZ controls, exact comparison with Protti $PROTTI_TAG)"
echo "  Theta(C13) >= $DEC13   [$THM13; prior: Protti $PROTTI13, BPZ $BPZ13]"
