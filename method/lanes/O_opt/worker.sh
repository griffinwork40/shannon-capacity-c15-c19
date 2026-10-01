#!/bin/sh
# usage: worker.sh "N EMAX MAXNODES TAG" ...   ; each job: search2 (<=7.5 min) + refine + exact (<=5 min)
cd "$(dirname "$0")"
PY=${PY:-../../.venv/bin/python}
export OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p logs
for job in "$@"; do
  set -- $job
  timeout 540 nice -n 10 $PY search2.py $1 12 8 $2 $3 $4 420 > logs/search_$4.log 2>&1
  timeout 300 nice -n 10 $PY exact_eval.py best_$4.json --refine > logs/exact_$4.log 2>&1
done
