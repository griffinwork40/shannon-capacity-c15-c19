#!/usr/bin/env python3
"""Exact comparison of our M (C13, dim p) with Protti's N (C13R8D522.lean, dim 522). stdlib only.
usage: compare_protti.py M_C13.txt C13R8D522.lean p"""
import re, sys
if hasattr(sys, 'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
M = int(open(sys.argv[1]).read().strip()); p = int(sys.argv[3])
src = open(sys.argv[2]).read()
N = int(re.search(r'^def N : Nat := (\d+)', src, re.M).group(1))
assert re.search(r'theorem alpha_ge : N ≤ \(strongPower \(SimpleGraph\.cycleGraph 13\) 522\)\.indepNum', src)
assert re.search(r'theorem capacity_lower : \(6\.302927046770772 : ℝ\) ≤ shannonCapacity \(SimpleGraph\.cycleGraph 13\)', src)
q = 522
print('Protti N: %d digits, dim %d; ours M: %d digits, dim %d' % (len(str(N)), q, len(str(M)), p))
win = M ** q > N ** p
print('EXACT: M^%d > N^%d (our root strictly larger): %s' % (q, p, win))
P = 6302927046770772
print('Protti decimal 6.302927046770772: P^q <= N*10^(15q): %s; (P+1)^q > N*10^(15q): %s'
      % (P ** q <= N * 10 ** (15 * q), (P + 1) ** q > N * 10 ** (15 * q)))
sys.exit(0 if win else 1)
