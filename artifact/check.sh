#!/bin/sh
# check.sh -- one-command check of
#     Theta(C15) >= 7.301635000991096   and   Theta(C19) >= 9.357203012726939
# in Lean 4 (Buys-Polak-Zuiddam framework) and with an independent Python evaluator.
#
#   sh check.sh [--install-elan] [--python-only] [--dir DIR]
#
#   --install-elan  if `lake` is not found, run the official elan installer with
#                   --no-modify-path (installs into ~/.elan; your shell profile is not edited)
#   --python-only   run steps 0-3 only (no Lean needed): bundle hashes, fresh clone, patch audit,
#                   independent Python evaluation; exits 0 on success. Not a substitute for the
#                   Lean check, which is the proof.
#   --dir DIR       work directory (default ./c15-c19-check); must not already contain
#                   shannon-capacity-lean/ (this script never deletes anything)
#
# Steps:
#   0. fingerprint the bundle files (certL2.patch, eval_dag.py, schedules/*.json);
#   1. clone github.com/spectra-research/shannon-capacity-lean into DIR, check out aa21eeb;
#   2. apply certL2.patch; verify the five new files and that the only change to an existing
#      BPZ file is five added import lines in ShannonBounds.lean;
#   3. Python (stdlib only): eval_dag.py re-derives tables, codes and base sizes from BPZ's
#      Lean sources, must reproduce BPZ's own CertC15 / CertC19 exactly (positive controls),
#      and must evaluate schedules/*.json to the same M as the Lean literals, digit for digit;
#   4. find lake (PATH, then ~/.elan/bin; --install-elan installs elan); check Lean version;
#   5. lake exe cache get ; lake build ShannonBounds.CapCertC15b ShannonBounds.CapCertC19c ;
#   6. fresh Lean process: re-type-check both statements verbatim, #print axioms, fail on
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
BUNDLE_SHA256="
certL2.patch:ee71e47141d59484fd77b7e9e096d0e1ad900d2553ffcaea8ce5377034ce448e
eval_dag.py:72d1b07af3a9e7d4a628112936d2047c8e99869fe169a603c0b4a7cccef442f3
schedules/best_C15_A_ref.json:6a37e3c9dd8170ca10d6d184ea5e76a25af1b29a23f10f69f7b8a9535113ff35
schedules/best_C19_C_ref.json:df340f3f1cdd6eace681e7d7e10801a151bde6c3837e12816d82d2b1c2948b92
"
FILES_SHA256="
ShannonBounds/DagTail.lean:f277d0b7695904f6339f760e6c37a51b40654d2b546e61d657bf268153efe147
ShannonBounds/CertC15b.lean:fd76961fc9d9ebf1d45b1d8f824250e37bd0f94701d694cf97a39779322ae9b9
ShannonBounds/CapCertC15b.lean:45b3b426ed9ee29ec553cfad72e9bcca7b7393bbe4fe01dd791872e07d435e6d
ShannonBounds/CertC19c.lean:c1d8209e7e628bc7556303f90c2c912fa68ba7c313f501ab2c1ce9246833b4ba
ShannonBounds/CapCertC19c.lean:d5d08a91559d8e5f93bfcaadb067f208a8bdc65d10e992018f6ab7e6c44f95b9
"
# sha256 of the decimal digits of M (no newline); equal to the Lean literals CertC15b.M / CertC19c.M
M15_SHA256="34e07ce861947b8cac30ca45a5d74cfc1b15ff100c4dcdb88923735ca5d3ad33"
M19_SHA256="ac85cbc50fb67faa4766e5f8426fe98552c29f8d6fc54165fc3c1cdebfa8203d"
DEC15="7.301635000991096"; DEC19="9.357203012726939"
BPZ15="7.301628695930103"; BPZ19="9.357200030000796"
THM15="ShannonBounds.CapCertC15b.shannonCapacity_cycleGraph_15_ge"
THM19="ShannonBounds.CapCertC19c.shannonCapacity_cycleGraph_19_ge"
NEW_IMPORTS="import ShannonBounds.DagTail
import ShannonBounds.CertC15b
import ShannonBounds.CapCertC15b
import ShannonBounds.CertC19c
import ShannonBounds.CapCertC19c"

HERE=$(cd "$(dirname "$0")" && pwd)
DIR="$(pwd)/c15-c19-check"
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
# digits of the Lean literal `def M : Nat :=` (next line), no newline
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
PATCH="$HERE/certL2.patch"

# ---------------------------------------------------------------- 1. clone + pin
BPZ="$DIR/shannon-capacity-lean"
if [ -e "$BPZ" ]; then fail "$BPZ already exists; pass --dir to a fresh directory (this script never deletes anything)"; fi
mkdir -p "$DIR"
DIR=$(cd "$DIR" && pwd)
BPZ="$DIR/shannon-capacity-lean"
say "1. cloning $BPZ_URL"
git clone "$BPZ_URL" "$BPZ"
cd "$BPZ"
git -c advice.detachedHead=false checkout "$BPZ_SHA"
HEAD_SHA=$(git rev-parse HEAD)
[ "$HEAD_SHA" = "$BPZ_SHA" ] || fail "HEAD is $HEAD_SHA, expected $BPZ_SHA"
echo "    HEAD = $HEAD_SHA ($(git log -1 --format='%ad %s' --date=iso))"
echo "    licence: $(head -n 2 LICENSE | tr -s ' ' | tr '\n' ' ')"
echo "    lean-toolchain: $(cat lean-toolchain)"
echo "    BPZ README rows: $(grep -E '^\| (15|19) \|' README.md | tr '\n' ' ')"

# ---------------------------------------------------------------- 2. patch
say "2. applying certL2.patch"
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
[ "$ADDED" = "$NEW_IMPORTS" ] || fail "ShannonBounds.lean: added lines are not exactly the five imports: $ADDED"
UNTRACKED=$(git ls-files --others --exclude-standard | sort | tr '\n' ' ')
[ "$UNTRACKED" = "ShannonBounds/CapCertC15b.lean ShannonBounds/CapCertC19c.lean ShannonBounds/CertC15b.lean ShannonBounds/CertC19c.lean ShannonBounds/DagTail.lean " ] \
  || fail "unexpected new files: $UNTRACKED"
echo "    only change to BPZ files: 5 import lines added to ShannonBounds.lean"
# The added files may not declare axioms or use features that let compiled code (and hence
# native_decide) disagree with the kernel. Comments are stripped crudely (-- and /- -/ lines);
# a false positive here fails loudly rather than silently.
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
cp "$HERE/eval_dag.py" "$PY/eval_dag.py"        # it writes M_C15.txt / M_C19.txt next to itself
PYLOG="$PY/eval_dag.log"
# eval_dag.py calls sys.set_int_max_str_digits(0); Pythons older than 3.11 (and unpatched 3.8-3.10,
# e.g. macOS /usr/bin/python3 3.9.6) have no digit limit and no such function, so a no-op is exact.
PYRUN='import sys, runpy
if not hasattr(sys, "set_int_max_str_digits"): sys.set_int_max_str_digits = lambda n: None
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")'
nice -n "$NICE" python3 -c "$PYRUN" "$PY/eval_dag.py" "$BPZ" \
  "$HERE/schedules/best_C15_A_ref.json" "$HERE/schedules/best_C19_C_ref.json" \
  --lean "$BPZ/ShannonBounds/CertC15b.lean" "$BPZ/ShannonBounds/CertC19c.lean" > "$PYLOG" 2>&1 \
  || { cat "$PYLOG"; fail "eval_dag.py exited nonzero"; }
cat "$PYLOG"
pyreq() { grep -F -- "$1" "$PYLOG" >/dev/null || fail "python: $2"; }
pyreq "CONTROL CertC15: 23 nodes, all node literals match: True; M == Lean M: True; p=3664 (README 3664); digits=3164 (README 3164); root=$BPZ15 (README $BPZ15) -> PASS" \
  "positive control BPZ CertC15 ($BPZ15) not reproduced exactly"
pyreq "CONTROL CertC19: 16 nodes, all node literals match: True; M == Lean M: True; p=11856 (README 11856); digits=11514 (README 11514); root=$BPZ19 (README $BPZ19) -> PASS" \
  "positive control BPZ CertC19 ($BPZ19) not reproduced exactly"
pyreq "root trunc15 = $DEC15 ; a^p <= M*10^(15p): True ; (a+1)^p > M*10^(15p): True" "C15 root is not $DEC15"
pyreq "root trunc15 = $DEC19 ; a^p <= M*10^(15p): True ; (a+1)^p > M*10^(15p): True" "C19 root is not $DEC19"
NOK=$(grep -c -F "Lean M == my M (digit for digit): True" "$PYLOG" || true)
[ "$NOK" = 2 ] || fail "python: Lean M == Python M reported for $NOK of 2 certificates"
NOK=$(grep -c -F "structural problems (S/children/exponents/tail args vs Rn defs): none" "$PYLOG" || true)
[ "$NOK" = 2 ] || fail "python: structural comparison with Lean clean for $NOK of 2 certificates"
NOK=$(grep -c -F "matches mine: True" "$PYLOG" || true)
[ "$NOK" = 2 ] || fail "python: CapCert decimal/exponents match for $NOK of 2 certificates"
for t in 15:CertC15b:$M15_SHA256 19:CertC19c:$M19_SHA256; do
  n=${t%%:*}; r=${t#*:}; cert=${r%%:*}; want=${r#*:}
  [ -f "$PY/M_C$n.txt" ] || fail "python did not write M_C$n.txt"
  tr -d '\n' < "$PY/M_C$n.txt" > "$PY/M_C$n.digits"
  lean_M "ShannonBounds/$cert.lean" > "$PY/M_lean_$cert.digits"
  cmp -s "$PY/M_C$n.digits" "$PY/M_lean_$cert.digits" || fail "Python M for C$n differs from Lean literal $cert.M"
  got=$(sha256 "$PY/M_C$n.digits")
  [ "$got" = "$want" ] || fail "C$n: sha256 of M is $got, expected $want"
  echo "    C$n: Python M == Lean $cert.M digit for digit ($(wc -c < "$PY/M_C$n.digits" | tr -d ' ') digits, sha256 $got)"
done
echo "    Python check OK"

if [ "$PYTHON_ONLY" = 1 ]; then
  say "PYTHON-ONLY CHECKS PASSED (steps 0-3; Lean steps 4-7 skipped by --python-only)"
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
  echo "    installing elan (official installer, --no-modify-path, no default toolchain)"
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$DIR/elan-init.sh"
  sh "$DIR/elan-init.sh" -y --no-modify-path --default-toolchain none
  LAKE="$EH/bin/lake"
  [ -x "$LAKE" ] || fail "elan install did not produce $LAKE"
  echo "    installed. Your shell PATH was NOT changed; to use Lean later:"
  echo "      export PATH=\"$EH/bin:\$PATH\""
else
  cat >&2 <<EOM

lake (the Lean build tool) was not found. Either re-run with --install-elan (runs the
official elan installer with --no-modify-path), or install elan yourself:

    curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

and re-run. elan fetches the Lean version pinned in lean-toolchain ($(cat lean-toolchain)).
Python check (step 3) already passed; the Lean check did not run.
EOM
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
say "5b. lake build ShannonBounds.CapCertC15b ShannonBounds.CapCertC19c"
T0=$(date +%s)
nice -n "$NICE" "$LAKE" build ShannonBounds.CapCertC15b ShannonBounds.CapCertC19c
echo "    build OK in $(( $(date +%s) - T0 )) s"

# ---------------------------------------------------------------- 6. statements + axioms
say "6. theorem statements and axioms (fresh Lean process on the built modules)"
PROBE="$DIR/probe_axioms.lean"
cat > "$PROBE" <<EOM
import ShannonBounds.CapCertC15b
import ShannonBounds.CapCertC19c
open SimpleGraph
#check @$THM15
#check @$THM19
-- the statements, restated verbatim and type-checked against the proofs:
example : ($DEC15 : ℝ) ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 15) :=
  $THM15
example : ($DEC19 : ℝ) ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 19) :=
  $THM19
#print ShannonBounds.shannonCapacity
#print axioms $THM15
#print axioms $THM19
EOM
OUT="$DIR/probe_axioms.out"
nice -n "$NICE" "$LAKE" env lean "$PROBE" > "$OUT" 2>&1 || { cat "$OUT"; fail "lean probe failed"; }
cat "$OUT"
if grep -E '(^|:)[0-9]+:[0-9]+: error' "$OUT" >/dev/null; then fail "lean probe reported an error"; fi
FLAT=$(tr '\n' ' ' < "$OUT" | tr -s ' ')
echo "$FLAT" | grep -F "shannonCapacity_cycleGraph_15_ge : $DEC15 ≤ ShannonBounds.shannonCapacity (cycleGraph 15)" >/dev/null \
  || fail "C15 theorem statement not as expected"
echo "    statement OK: ($DEC15 : ℝ) ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 15)"
echo "$FLAT" | grep -F "shannonCapacity_cycleGraph_19_ge : $DEC19 ≤ ShannonBounds.shannonCapacity (cycleGraph 19)" >/dev/null \
  || fail "C19 theorem statement not as expected"
echo "    statement OK: ($DEC19 : ℝ) ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 19)"
NLIST=$(grep -c "depends on axioms" "$OUT" || true)
[ "$NLIST" = 2 ] || fail "#print axioms produced $NLIST axiom lists, expected 2"
if grep -F "sorryAx" "$OUT" >/dev/null; then fail "a theorem depends on sorryAx"; fi
BAD=$(sed -n '/depends on axioms/,$p' "$OUT" | tr -d '[],' | tr ' ' '\n' | sed 's/^ *//' \
      | grep -v -e '^$' -e "^'" -e '^depends$' -e '^on$' -e '^axioms:$' \
                -e '^propext$' -e '^Classical\.choice$' -e '^Quot\.sound$' \
                -e '\._native\.native_decide\.ax_[0-9_]*$' || true)
[ -z "$BAD" ] || fail "unexpected axioms: $BAD"
for t in 15 19; do
  NAX=$(awk -v t="cycleGraph_${t}_ge'" 'index($0,t)&&/depends on axioms/{on=1} on{print} on&&/\]/{exit}' "$OUT" \
        | grep -o '_native\.native_decide\.ax_[0-9_]*' | wc -l | tr -d ' ')
  echo "    axioms OK (C$t): propext, Classical.choice, Quot.sound + $NAX native_decide auxiliary axioms; no sorryAx"
done

# ---------------------------------------------------------------- 7. sorry grep
say "7. grep for sorry/admit in all Lean sources"
if grep -rnw --include='*.lean' -e sorry -e admit ShannonBounds ShannonBounds.lean; then
  fail "found sorry/admit in the Lean sources (listed above)"
fi
echo "    no sorry/admit in ShannonBounds/*.lean or ShannonBounds.lean"

say "summary: BPZ $BPZ_SHA + certL2.patch; $LAKE_V; Mathlib $MATHLIB_REV; finished $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "ALL CHECKS PASSED (Lean 4 build + statements + axioms, and independent Python with exact BPZ controls)"
echo "  Theta(C15) >= $DEC15   [$THM15; BPZ: $BPZ15]"
echo "  Theta(C19) >= $DEC19   [$THM19; BPZ: $BPZ19]"
