#!/usr/bin/env python3
"""Rebuild dist/shannon-C15-C19-v1.0.tar.gz deterministically from artifact/.

Same input files -> byte-identical tarball (sorted names, fixed mtime/owner/mode, gzip mtime 0),
so anyone can confirm the release asset equals the artifact/ directory of tag v1.0:
    python3 tools/make_dist.py && shasum -a 256 -c dist/SHA256   (run from the repo root)
"""
import gzip, hashlib, io, os, tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, NAME = os.path.join(ROOT, "artifact"), "shannon-C15-C19"
OUT = os.path.join(ROOT, "dist", NAME + "-v1.0.tar.gz")
MTIME = 1790812800  # 2026-10-01T00:00:00Z

def info(name, size=None, is_dir=False):
    ti = tarfile.TarInfo(name)
    ti.mtime, ti.uid, ti.gid, ti.uname, ti.gname = MTIME, 0, 0, "", ""
    if is_dir:
        ti.type, ti.mode = tarfile.DIRTYPE, 0o755
    else:
        ti.size, ti.mode = size, 0o644
    return ti

entries = []
for dp, dns, fns in os.walk(SRC):
    dns.sort()
    rel = os.path.relpath(dp, SRC)
    entries.append((NAME if rel == "." else NAME + "/" + rel.replace(os.sep, "/"), None))
    for f in sorted(fns):
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
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as fh:
    with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0, compresslevel=9) as gz:
        gz.write(raw.getvalue())
digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
with open(os.path.join(ROOT, "dist", "SHA256"), "w") as fh:
    fh.write(f"{digest}  {os.path.basename(OUT)}\n")
print(digest, os.path.relpath(OUT, ROOT))
