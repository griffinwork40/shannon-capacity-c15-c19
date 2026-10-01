#!/usr/bin/env python3
"""Build shannon-C13-v1.1.tar.gz deterministically from a bundle directory.

    python3 make_dist_c13.py SRC_DIR OUT_DIR

Same rules as the v1.0 tools/make_dist.py (sorted names, fixed mtime/owner/mode, gzip mtime 0),
so the same input files always give a byte-identical tarball. Writes OUT_DIR/shannon-C13-v1.1.tar.gz
and OUT_DIR/SHA256. Skips work directories (c13-check/) and __pycache__.
"""
import gzip, hashlib, io, os, sys, tarfile

SRC, OUTD = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
NAME = "shannon-C13"
OUT = os.path.join(OUTD, NAME + "-v1.1.tar.gz")
MTIME = 1790812800  # 2026-10-01T00:00:00Z, as v1.0
SKIP = {"c13-check", "__pycache__"}


def info(name, size=None, is_dir=False, mode=0o644):
    ti = tarfile.TarInfo(name)
    ti.mtime, ti.uid, ti.gid, ti.uname, ti.gname = MTIME, 0, 0, "", ""
    if is_dir:
        ti.type, ti.mode = tarfile.DIRTYPE, 0o755
    else:
        ti.size, ti.mode = size, mode
    return ti


entries = []
for dp, dns, fns in os.walk(SRC):
    dns[:] = sorted(d for d in dns if d not in SKIP)
    rel = os.path.relpath(dp, SRC)
    entries.append((NAME if rel == "." else NAME + "/" + rel.replace(os.sep, "/"), None))
    for f in sorted(fns):
        if f == ".DS_Store":
            continue
        entries.append((NAME + "/" + os.path.relpath(os.path.join(dp, f), SRC).replace(os.sep, "/"),
                        os.path.join(dp, f)))
raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as tf:
    for name, path in sorted(entries):
        if path is None:
            tf.addfile(info(name, is_dir=True))
        else:
            data = open(path, "rb").read()
            tf.addfile(info(name, len(data)), io.BytesIO(data))
os.makedirs(OUTD, exist_ok=True)
with open(OUT, "wb") as fh:
    with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0, compresslevel=9) as gz:
        gz.write(raw.getvalue())
digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
with open(os.path.join(OUTD, "SHA256"), "w") as fh:
    fh.write(f"{digest}  {os.path.basename(OUT)}\n")
print(digest, OUT)
