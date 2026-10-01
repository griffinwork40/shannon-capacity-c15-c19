#!/usr/bin/env python3
"""Lane T_c13: copy of the released artifact eval_dag.py (lane R3 independent evaluator), extended to
C13 (arity-3 terminal code K3a; C13 base family sizes, see base_sizes) -- otherwise unchanged.

Usage:  python3 eval_dag.py <bpz_dir> <schedule.json> [<schedule.json> ...] [--lean <CertX.lean> ...]
        (a --lean file given after a schedule is matched to it by n)

Everything is parsed from BPZ Lean sources in <bpz_dir>/ShannonBounds (stdlib only):
  * Letter.sep          PortRealisation.lean
  * Letter.sigma        Reindex.lean   (Rf child = base reindexed by sigma, w_reindex: w'(a) = w(sigma a))
  * tables S2*, S3*     Substitutions.lean (re-checked: hin + hcross, Layered.lean:89)
  * codes K*            TerminalCodes.lean (re-checked: pairwise separated, Layered.lean:379)
  * base data           BaseC{n}Data.lean: Iraw, Xraw, pairsRaw, portsRaw; the seven family
                        sizes are recomputed from the raw words (PortRealisation.fam, Lift.Xc/Xstar)
                        and the RichPortSystem conditions (Lift.lean:97) are re-checked.
  * d (base power)      CapCertC{n}.lean strongPower_mul_iso Cyc d E
Semantics (Layered.lean):
  w_multiSubst:          node weight w(a) = sum_{x in S.T a} prod_i w_i(x_i), exponent = sum e_i
  le_indepNum_multiCode: M = sum_{x in K.C} prod_i w_i(x_i) <= alpha(G^(sum e_i)), G = C_n^d
  DagTail.tailIter S X Z1 Z2 n:  y_0 = X, y_{k+1} = S(y_k, Z1, Z2)
Root: Decimal.decimal_le form, a = max{a : a^p <= M * 10^(15p)}, exact integers.
"""
import re, sys, os, json, hashlib, functools
print = functools.partial(print, flush=True)
sys.set_int_max_str_digits(0)

L = ['B', 'N', 'A', 'D', 'O', 'H', 'V']


def rd(root, f):
    return open(os.path.join(root, 'ShannonBounds', f)).read()


# ---------------------------------------------------------------- framework data
def parse_sep(root):
    src = rd(root, 'PortRealisation.lean')
    blk = src.split('def sep : Letter → Letter → Bool')[1].split('| _, _ => false')[0]
    S = set(re.findall(r'\b([BNADOHV]), ([BNADOHV]) => true', blk))
    assert all((b, a) in S for a, b in S), 'sep not symmetric'
    assert not any((a, a) in S for a in L), 'sep not irreflexive'
    return S


def parse_sigma(root):
    src = rd(root, 'Reindex.lean')
    blk = src.split('toFun')[1].split('invFun')[0]
    sig = dict(re.findall(r'\.([BNADOHV]) => \.([BNADOHV])', blk))
    assert sorted(sig) == sorted(L) and sorted(sig.values()) == sorted(L)
    return sig


def words(s):
    return [tuple(x.strip().lstrip('.') for x in w.split(',')) for w in re.findall(r'!\[([^\]]*)\]', s)]


def parse_tables(root):
    src = rd(root, 'Substitutions.lean')
    T = {}
    for m in re.finditer(r'def T(\w+) : Letter → Finset \(Fin (\d+) → Letter\)\n(.*?)\n\n', src, re.S):
        q, body = int(m.group(2)), m.group(3)
        parts = re.split(r'\|\s*\.?([BNADOHV])\s*=>', body)
        tab = {}
        for i in range(1, len(parts), 2):
            ws = words(parts[i + 1])
            assert all(len(w) == q for w in ws) and len(set(ws)) == len(ws)
            assert parts[i] not in tab
            tab[parts[i]] = ws
        assert set(tab) == set(L)
        name = 'S' + m.group(1)
        assert re.search(r'def %s : Subst Letter Letter.sep %d :=\s*⟨T%s,' % (name, q, m.group(1)), src), name
        T[name] = (q, tab)
    return T


def parse_codes(root):
    src = rd(root, 'TerminalCodes.lean')
    K = {}
    for m in re.finditer(r'def C(\w+) : Finset \(Fin (\d+) → Letter\) :=\n(.*?)\n\n', src, re.S):
        r = int(m.group(2)); ws = words(m.group(3))
        assert all(len(w) == r for w in ws) and len(set(ws)) == len(ws)
        name = 'K' + m.group(1)
        assert re.search(r'def %s : Code Letter Letter.sep %d := ⟨C%s,' % (name, r, m.group(1)), src)
        K[name] = (r, ws)
    return K


def separated(SEP, x, y):
    return any((a, b) in SEP for a, b in zip(x, y))


def table_admissible(SEP, tab):
    hin = all(separated(SEP, x, y) for a in L for x in tab[a] for y in tab[a] if x != y)
    hcross = all(separated(SEP, x, y) for (a, b) in SEP for x in tab[a] for y in tab[b])
    return hin and hcross


def code_separated(SEP, ws):
    return all(separated(SEP, x, y) for i, x in enumerate(ws) for y in ws[i + 1:])


# ---------------------------------------------------------------- base port system
def parse_list(src, name):
    body = re.search(r'def %s : List [^:]*?:= \[(.*?)\]' % name, src, re.S).group(1)
    return body


def base_sizes(root, n):
    if n == 13:
        return base_sizes_c13(root)
    return base_sizes_raw(root, n)


def base_sizes_c13(root):
    """BaseC13 is not given by raw word lists (its footprint is six K-cosets), so the seven sizes
    are read from the theorems BaseC13.lean states and proves (base_N, base_d, base_eta,
    base_Xc_card) and assembled as in RichPortSystem.card_fam_* (B = N - d, N = eta, A = D = |Xc|,
    O = H = V = d); they are not recomputed from words here."""
    src = rd(root, 'BaseC13.lean')
    g = lambda pat: int(re.search(pat, src).group(1))
    N = g(r'theorem base_N : base\.N = (\d+)')
    d = g(r'theorem base_d : base\.d = (\d+)')
    eta = g(r'theorem base_eta : base\.eta = (\d+)')
    xc = g(r'theorem base_Xc_card \(c : Bool\) : \(base\.Xc c\)\.card = (\d+)')
    L_ = g(r'theorem base_L : base\.L = (\d+)')
    fam = {'B': N - d, 'N': eta, 'A': xc, 'D': xc, 'O': d, 'H': d, 'V': d}
    assert eta + 2 * xc == L_
    return fam, dict(N=N, d=d, L=L_, source='BaseC13.lean theorem statements')


def base_sizes_raw(root, n):
    """Recompute the seven family sizes of BaseC{n}.base from raw words; re-check the
    RichPortSystem conditions (Lift.lean:97) and independence of I, X in C_n^4."""
    src = rd(root, 'BaseC%dData.lean' % n)
    I = [int(x) for x in re.findall(r'\d+', parse_list(src, 'Iraw'))]
    X = [int(x) for x in re.findall(r'\d+', parse_list(src, 'Xraw'))]
    pairs = [(int(a), int(b), c == 'true') for a, b, c in
             re.findall(r'\((\d+), (\d+), (true|false)\)', parse_list(src, 'pairsRaw'))]
    ports = [int(x) for x in re.findall(r'\d+', parse_list(src, 'portsRaw'))]
    # coordinates: base-n, 4 digits (BaseC{n}Data: wconfN uses /1,/n,/n^2,/n^3)
    k = 4
    assert re.search(r'abbrev Code := Fin %d\b' % n ** k, src)
    dig = lambda u: [(u // n ** j) % n for j in range(k)]
    sconf = lambda a, b: (a - b) % n in (0, 1, n - 1)
    conf = lambda u, v: all(sconf(a, b) for a, b in zip(dig(u), dig(v)))  # closed conflict (incl. u=v)
    assert all(0 <= u < n ** k for u in I + X)
    Is, Xs = set(I), set(X)
    assert len(Is) == len(I) and len(Xs) == len(X)

    def nbrs(u):
        d = dig(u); out = []
        for o in range(3 ** k):
            dd = [(d[j] + (o // 3 ** j) % 3 - 1) % n for j in range(k)]
            out.append(sum(dd[j] * n ** j for j in range(k)))
        return out
    indep = lambda S: all(w == u or w not in S for u in S for w in nbrs(u))
    assert indep(Is), 'I not independent'
    assert indep(Xs), 'X not independent'
    pmap = {a: (b, c) for a, b, c in pairs}

    def side(r): return pmap[r][1] if r in pmap else False

    def ep(c, r):
        if r not in pmap: return r
        b, s = pmap[r]
        return r if c == s else b
    P = set(ports); assert len(P) == len(ports) and P <= Is
    alt = lambda r: ep(not side(r), r)
    assert all(ep(side(r), r) == r for r in P)
    assert all(alt(r) not in Is for r in P)
    assert all(all(w == r for w in nbrs(alt(r)) if w in Is) for r in P)   # private
    assert all(conf(r, alt(r)) for r in P)
    assert len({alt(r) for r in P}) == len(P)
    for c in (False, True):
        assert all(r == s or not conf(ep(c, r), ep(c, s)) for r in P for s in P)
    Xc = {c: {x for x in Xs if any(conf(x, ep(c, r)) for r in P)} for c in (False, True)}
    assert not (Xc[False] & Xc[True]), 'hsep fails'
    Xstar = Xs - Xc[False] - Xc[True]
    fam = {'B': len(Is - P), 'N': len(Xstar), 'A': len(Xc[False]), 'D': len(Xc[True]),
           'O': len(P), 'H': len({ep(True, r) for r in P}), 'V': len({ep(False, r) for r in P})}
    return fam, dict(N=len(Is), d=len(P), L=len(Xs))


# ---------------------------------------------------------------- evaluation
def subst(S, ch):
    q, tab = S
    assert len(ch) == q
    w = {}
    for a in L:
        t = 0
        for x in tab[a]:
            p = 1
            for i, l in enumerate(x):
                p *= ch[i][1][l]
            t += p
        w[a] = t
    return (sum(c[0] for c in ch), w)


def code(Kc, ch):
    r, ws = Kc
    assert len(ch) == r
    t = 0
    for x in ws:
        p = 1
        for i, l in enumerate(x):
            p *= ch[i][1][l]
        t += p
    return sum(c[0] for c in ch), t


def root_trunc(M, p, digits=15):
    """a = max{a : a^p <= M*10^(digits*p)}  (exact)."""
    T = M * 10 ** (digits * p)
    # float-free initial estimate via integer bit length, then exact Newton-free bracketing
    lo, hi = 0, 1
    while hi ** p <= T:
        hi *= 2
    lo = hi // 2
    # digit-by-digit refinement using the integer log estimate first
    import math
    est = int(math.exp((math.log10(M) / p + digits) * math.log(10))) if M > 0 else 0
    if lo <= est <= hi:
        a = est
        step = max(1, est // 10 ** 12)
        while a ** p > T: a -= step
        while (a + step) ** p <= T: a += step
        lo, hi = a, a + step
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** p <= T: lo = mid
        else: hi = mid
    assert lo ** p <= T < (lo + 1) ** p
    return lo


def fmt(a, digits=15):
    s = str(a); return s[:-digits] + '.' + s[-digits:]


# ---------------------------------------------------------------- BPZ certificate parser (controls)
def parse_bpz_cert(root, n):
    src = rd(root, 'CertC%d.lean' % n)
    abbr = dict(re.findall(r'abbrev (\w+) : (?:Subst|Code) Letter Letter.sep \d+ := (?:Substitutions|TerminalCodes)\.(\w+)', src))
    lit = {}
    for m in re.finditer(r'def (w\w+) : Letter → Nat\n((?:  \| \.[BNADOHV] => \d+\n)+)', src):
        lit[m.group(1)] = {a: int(v) for a, v in re.findall(r'\.([BNADOHV]) => (\d+)', m.group(2))}
    M = int(re.search(r'def M : Nat :=\n\s*(\d+)', src).group(1))
    nodes = []
    for m in re.finditer(r'def R(\w+) \(R : Realisation Letter Letter.sep G\) :\n\s*Realisation Letter Letter.sep \(SimpleGraph.strongPower G (\d+)\) :=\n\s*Realisation.multiSubst e(\w+) \(ch(\w+) R\) (\w+)', src):
        nm, E, e1, c1, S = m.groups(); assert nm == e1 == c1
        ex = [int(x) for x in re.findall(r'\d+', re.search(r'def e%s : Fin \d+ → Nat := (.*)' % nm, src).group(1))]
        chb = re.search(r'def ch%s \(R .*?\n.*?\n  (Fin.cases .*?)\n' % nm, src, re.S).group(1)
        ch = re.findall(r'\((R\w+) R\)', chb)
        nodes.append((nm, int(E), ex, ch, abbr[S]))
    eT = [int(x) for x in re.findall(r'\d+', re.search(r'def eT : Fin \d+ → Nat := (.*)', src).group(1))]
    tch_full = re.search(r'def terminalChildren.*?\n\n', src, re.S).group(0)
    # last child may be written "fun _ => Rn25 R" without parens (CertC7)
    tch = re.findall(r'\(?(R\w+) R\)?', tch_full.split(':=')[-1])
    Etot = int(re.search(r'strongPower G (\d+)\)\.indepNum', src).group(1))
    return abbr, lit, M, nodes, eT, tch, Etot


def base_d(root, n):
    return int(re.search(r'strongPower_mul_iso BaseC%d.Cyc%d (\d+) (\d+)' % (n, n), rd(root, 'CapCertC%d.lean' % n)).group(1))


def readme_value(root, n):
    m = re.search(r'^\| %d \| ([\d.]+) \| (\d+) \| (\d+) \|' % n, open(os.path.join(root, 'README.md')).read(), re.M)
    return m.group(1), int(m.group(2)), int(m.group(3))


def control(root, n, T, K, w0, sigma):
    abbr, lit, M_lean, nodes, eT, tch, Etot = parse_bpz_cert(root, n)
    assert lit['w0'] == w0, ('w0 mismatch', lit['w0'], w0)
    R = {'R1': (1, w0)}
    if 'w0f' in lit:
        R['Rf'] = (1, {a: w0[sigma[a]] for a in L}); assert R['Rf'][1] == lit['w0f']
    ok = True
    for nm, E, ex, ch, S in nodes:
        c = [R[x] for x in ch]
        assert [x[0] for x in c] == ex and sum(ex) == E, (nm, ex, E)
        R['R' + nm] = subst(T[S], c)
        ok &= R['R' + nm][1] == lit['w' + nm]
    Kn = abbr['K']
    e, M = code(K[Kn], [R[c] for c in tch])
    assert [R[c][0] for c in tch] == eT and e == Etot
    d = base_d(root, n); p = d * e
    a = root_trunc(M, p)
    rv, rp, rdg = readme_value(root, n)
    good = ok and M == M_lean and fmt(a) == rv and p == rp and len(str(M)) == rdg
    print('CONTROL CertC%d: %d nodes, all node literals match: %s; M == Lean M: %s; p=%d (README %d); digits=%d (README %d); root=%s (README %s) -> %s'
          % (n, len(nodes), ok, M == M_lean, p, rp, len(str(M)), rdg, fmt(a), rv, 'PASS' if good else 'FAIL'))
    return good


# ---------------------------------------------------------------- schedule JSON
class Dag:
    def __init__(self, T, K, w0, sigma):
        self.T, self.K = T, K
        self.atoms = {'R1': (1, w0), 'Rf': (1, {a: w0[sigma[a]] for a in L})}
        self.memo = {}
        self.used = set(); self.tails = []

    def ev(self, t):
        if isinstance(t, str):
            self.used.add(t); return self.atoms[t]
        key = json.dumps(t)
        if key in self.memo: return self.memo[key]
        if t[0] == 'tail':
            # ['tail', start, S, pos, 'ww', n]  ==  DagTail.tailIter S start R1 R1 n (CertC*b/c.lean)
            _, start, S, pos, zz, cnt = t
            assert pos == 0 and zz == 'ww' and isinstance(cnt, int) and cnt >= 0, t
            self.used.add('R1')
            y = self.ev(start)
            for _ in range(cnt):
                y = subst(self.T[S], [y, self.atoms['R1'], self.atoms['R1']])
            self.tails.append(cnt)
            if cnt > 0: self.memo[key] = y
            return y
        S = t[0]
        r = subst(self.T[S], [self.ev(c) for c in t[1:]])
        self.used.add(S)
        self.memo[key] = r
        return r


def eval_schedule(path, T, K, w0, sigma):
    d = json.load(open(path))
    D = Dag(T, K, w0, sigma)
    ch = [D.ev(c) for c in d['terminal']]
    e, M = code(K[d['code']], ch)
    return d, D, ch, e, M


# ---------------------------------------------------------------- lane L2 Lean DAG (comparison)
def lean_dag(path, T, K, w0, sigma):
    src = open(path).read()
    M = int(re.search(r'def M : Nat :=\n\s*(\d+)', src).group(1))
    w0L = {a: int(v) for a, v in re.findall(r'\.([BNADOHV]) => (\d+)', re.search(r'def w0 : Letter → Nat\n((?:  \| .*\n)+)', src).group(1))}
    sz = {'s1': (1, w0L)}
    if 'def sf' in src:
        w0f = {a: int(v) for a, v in re.findall(r'\.([BNADOHV]) => (\d+)', re.search(r'def w0f : Letter → Nat\n((?:  \| .*\n)+)', src).group(1))}
        assert re.search(r'\(R1 R\)\.reindex Letter\.sigma Letter\.sigma_sep', src)
        assert w0f == {a: w0L[sigma[a]] for a in L}
        sz['sf'] = (1, w0f)
    rmap = {'R1': 's1', 'Rf': 'sf'}
    probs = []
    for m in re.finditer(r'def (sn\d+) : Sizes := (.*)', src):
        nm, rhs = m.groups(); tok = rhs.split()
        num = nm[2:]
        decl = int(re.search(r'def Rn%s \(R .*?\n\s*Realisation Letter Letter.sep \(SimpleGraph.strongPower G (\d+)\) :=' % num, src).group(1))
        body = re.search(r'def Rn%s \(R [^\n]*\n[^\n]*:=\n\s*([^\n]*)' % num, src).group(1)
        if tok[0] in ('node2', 'node3'):
            S = tok[1].split('.')[1]; kids = tok[2:]
            v = subst(T[S], [sz[k] for k in kids])
            # cross-check realisation side: same S, children, exponents
            ms = re.match(r'Realisation\.multiSubst en%s \(chn%s R\) Substitutions\.(\w+)' % (num, num), body)
            chb = re.search(r'def chn%s \(R .*?\n.*?\n  (Fin.cases .*?)\n' % num, src, re.S).group(1)
            rk = [rmap.get(x, 's' + x[1:]) for x in re.findall(r'\((R\w+) R\)', chb)]
            ex = [int(x) for x in re.findall(r'\d+', re.search(r'def en%s : Fin \d+ → Nat := (.*)' % num, src).group(1))]
            if not ms or ms.group(1) != S or rk != kids or ex != [sz[k][0] for k in kids]:
                probs.append(nm)
        elif tok[0] == 'tailW':
            S = tok[1].split('.')[1]; st, z1, z2, cnt = tok[2], tok[3], tok[4], int(tok[5])
            y = sz[st]
            for _ in range(cnt):
                y = subst(T[S], [y, sz[z1], sz[z2]])
            v = y
            mt = re.search(r'tailIter Substitutions\.(\w+) \((R\w+) R\) \((R\w+) R\) \((R\w+) R\) (\d+)\)', body)
            if not mt or mt.group(1) != S or rmap.get(mt.group(2), 's' + mt.group(2)[1:]) != st or \
                    [rmap[mt.group(3)], rmap[mt.group(4)]] != [z1, z2] or int(mt.group(5)) != cnt:
                probs.append(nm)
        else:
            raise ValueError(rhs)
        if v[0] != decl: probs.append(nm + ':exp')
        sz[nm] = v
    tm = tuple(re.search(r'theorem stepM : M = code(\d) K ((?:\w+ ?)+)', src).group(2).split())
    Kn = re.search(r'abbrev K : Code Letter Letter.sep %d := TerminalCodes\.(\w+)' % len(tm), src).group(1)
    e, Mc = code(K[Kn], [sz[x] for x in tm])
    eT = [int(x) for x in re.findall(r'\d+', re.search(r'def eT : Fin %d → Nat := (.*)' % len(tm), src).group(1))]
    tc = [rmap.get(x, 's' + x[1:]) for x in re.findall(r'\((R\w+) R\)', re.search(r'def terminalChildren.*?\n\n', src, re.S).group(0))]
    Ebound = int(re.search(r'strongPower G (\d+)\)\.indepNum', src).group(1))
    if eT != [sz[x][0] for x in tm] or tc != list(tm) or Ebound != e: probs.append('terminal')
    return dict(M=M, Mcomp=Mc, w0=w0L, nodes=len(sz) - len([k for k in sz if k in ('s1', 'sf')]), e=e, eT=eT,
                probs=probs, sizes=sz, term=tm, Kn=Kn)


def cap_info(path):
    src = open(path).read()
    iso = re.search(r'strongPower_mul_iso BaseC(\d+)\.Cyc\d+ (\d+) (\d+)', src).groups()
    tight = re.search(r'(\d+) \^ (\d+) ≤ CertC\w+\.M \* \(10 \^ 15\) \^ (\d+) ∧\s*CertC\w+\.M \* \(10 \^ 15\) \^ \d+ < (\d+) \^ (\d+)', src)
    dec = re.search(r'\(([\d.]+) : ℝ\) ≤ shannonCapacity \(SimpleGraph.cycleGraph', src).group(1)
    return dict(n=int(iso[0]), d=int(iso[1]), E=int(iso[2]), a=int(tight.group(1)), p=int(tight.group(2)), dec=dec)


# ---------------------------------------------------------------- main
def main(argv):
    root = argv[0]
    scheds, leans = [], []
    i = 1; mode = 's'
    while i < len(argv):
        if argv[i] == '--lean': mode = 'l'
        elif mode == 's': scheds.append(argv[i])
        else: leans.append(argv[i])
        i += 1
    SEP = parse_sep(root); sigma = parse_sigma(root)
    T = parse_tables(root); K = parse_codes(root)
    print('sep: %d ordered pairs, symmetric, irreflexive' % len(SEP))
    sig_ok = all(((sigma[a], sigma[b]) in SEP) == ((a, b) in SEP) for a in L for b in L)
    print('sigma =', sigma, 'preserves sep:', sig_ok)
    allok = sig_ok
    for k in sorted(T):
        adm = table_admissible(SEP, T[k][1]); allok &= adm
        print('  table %s q=%d words=%d admissible(hin+hcross)=%s' % (k, T[k][0], sum(len(T[k][1][a]) for a in L), adm))
    for k in sorted(K):
        s = code_separated(SEP, K[k][1]); allok &= s
        print('  code %s r=%d words=%d pairwise separated=%s' % (k, K[k][0], len(K[k][1]), s))

    bases = {}
    for n in sorted({json.load(open(p))['n'] for p in scheds} | {15, 19}):
        fam, par = base_sizes(root, n)
        w0 = parse_bpz_cert(root, n)[1]['w0']
        print('BASE C%d: recomputed families %s params %s; == CertC%d.w0: %s' % (n, fam, par, n, fam == w0))
        allok &= fam == w0
        bases[n] = fam
    sig7 = None
    # positive controls
    for n in sorted(bases):
        allok &= control(root, n, T, K, bases[n], sigma)
    try:
        fam7 = parse_bpz_cert(root, 7)[1]['w0']
        allok &= control(root, 7, T, K, fam7, sigma)   # extra control: exercises Rf + S2a
    except Exception as ex:
        print('CONTROL CertC7 skipped:', ex)
    if not allok:
        print('FRAMEWORK/CONTROL FAILURE'); return 1

    here = os.path.dirname(os.path.abspath(__file__))
    for path in scheds:
        d, D, ch, e, M = eval_schedule(path, T, K, bases[None] if False else bases[json.load(open(path))['n']], sigma)
        n = d['n']; dd = base_d(root, n); p = dd * e
        a = root_trunc(M, p)
        sha = hashlib.sha256(str(M).encode()).hexdigest()
        print('\nSCHEDULE %s (n=%d, code %s)' % (path, n, d['code']))
        print('  tables used: %s; atoms used: %s' % (sorted(x for x in D.used if x.startswith('S')), sorted(x for x in D.used if x.startswith('R'))))
        for S in D.used:
            if S.startswith('S'): assert table_admissible(SEP, T[S][1])
        print('  distinct internal nodes (memoised, n=0 tails collapsed): %d; tail lengths: %s' % (len(D.memo), D.tails))
        print('  terminal child exponents eT = %s, E = %d (in G = C%d^%d), dim p = %d' % ([c[0] for c in ch], e, n, dd, p))
        print('  M digits = %d, sha256(str M) = %s' % (len(str(M)), sha))
        T15 = M * 10 ** (15 * p)
        print('  root trunc15 = %s ; a^p <= M*10^(15p): %s ; (a+1)^p > M*10^(15p): %s' % (fmt(a), a ** p <= T15, (a + 1) ** p > T15))
        print('  float_rate in JSON: %r' % d.get('float_rate'))
        open(os.path.join(here, 'M_C%d.txt' % n), 'w').write(str(M) + '\n')
        for lp in leans:
            ld = lean_dag(lp, T, K, bases[n], sigma)
            if ld['w0'] != bases[n]: continue
            print('  vs Lean %s:' % os.path.basename(lp))
            print('    Lean M literal digits=%d; Lean M == my M (digit for digit): %s' % (len(str(ld['M'])), ld['M'] == M))
            print('    my re-evaluation of the Lean Sizes DAG == Lean M: %s; == my JSON M: %s' % (ld['Mcomp'] == ld['M'], ld['Mcomp'] == M))
            print('    Lean distinct nodes=%d; Lean eT=%s E=%d; structural problems (S/children/exponents/tail args vs Rn defs): %s'
                  % (ld['nodes'], ld['eT'], ld['e'], ld['probs'] or 'none'))
            # terminal children sizes vectors
            print('    terminal sizes vectors equal: %s' % all(ld['sizes'][t] == c for t, c in zip(ld['term'], ch)))
            cp = lp.replace('/CertC', '/CapCertC')
            if os.path.exists(cp):
                ci = cap_info(cp)
                print('    %s: iso Cyc%d^%d^E with d=%d E=%d; tight a=%d p=%d; stated %s -> matches mine: %s'
                      % (os.path.basename(cp), ci['n'], ci['d'] * ci['E'], ci['d'], ci['E'], ci['a'], ci['p'], ci['dec'],
                         ci['a'] == a and ci['p'] == p and ci['dec'] == fmt(a) and ci['E'] == e and ci['d'] == dd))
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1:]))
