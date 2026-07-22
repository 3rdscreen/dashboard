#!/usr/bin/env python3
"""
OOK pre-delivery audit. Catches the #1 recurring bug class: a display store that
silently went stale because an ingest step was skipped or shortcut. Pure-data, offline.
Exit 0 = safe to deliver. Exit 1 = DO NOT deliver (a panel is stale/broken).
Usage: python3 verify_ook.py /mnt/user-data/outputs/ook.html
"""
import re, json, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs/ook.html'
C = open(PATH).read()
FAILS, WARNS = [], []
def fail(m): FAILS.append(m)
def warn(m): WARNS.append(m)

MO = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
def dkey(s):
    p = s.split()
    if len(p) < 2 or p[0] not in MO: return None      # e.g. 'MTD Mar 1-16' aggregate rows
    try: return (MO[p[0]], int(p[1]))
    except ValueError: return None

def brace_obj(anchor_regex, start=0):
    """Return JSON-parsed object whose opening { follows the anchor."""
    m = re.search(anchor_regex, C[start:])
    if not m: return None
    i = C.index('{', start + m.end()); depth = 0; j = i
    while j < len(C):
        if C[j] == '{': depth += 1
        elif C[j] == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    return json.loads(C[i:j+1])

def brace_after(token):
    """Parse the object literal that opens right after a bare `token:` inside GRANULAR."""
    k = C.index(token); i = C.index('{', k); depth = 0; j = i
    while j < len(C):
        if C[j] == '{': depth += 1
        elif C[j] == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    return json.loads(C[i:j+1])

# ---- load core ----
D = brace_obj(r'const D\s*=\s*')
LATEST = max((e['d'] for e in D['meta']), key=dkey)
print(f"LATEST DATE (from D.meta) = {LATEST}\n")

# ALL_DATES (drives the date picker) must reach LATEST
mad=re.search(r'ALL_DATES\s*=\s*\[(.*?)\]',C,re.S)
if mad:
    ad=[x.strip().strip('"') for x in mad.group(1).split(',')]
    ad=[x for x in ad if x]
    if ad and ad[-1]!=LATEST:
        fail(f"ALL_DATES ends at {ad[-1]}, expected {LATEST} — date picker will not reach the latest day")
    else:
        print(f"ALL_DATES tail = {ad[-1] if ad else None}  (date picker reaches latest)")
else:
    warn("ALL_DATES array not found")


def maxdate_list(lst):
    ds=[e['d'] for e in lst if dkey(e['d'])]; return max(ds,key=dkey) if ds else None
def dup_dates(lst):
    ds = [e['d'] for e in lst if dkey(e['d'])]; return sorted({d for d in ds if ds.count(d) > 1})

# ============ 1. FRESHNESS TABLE: every store's latest date must == LATEST ============
print("== STORE FRESHNESS (latest date each store carries) ==")
rows = []

# account-level D
for p in ['meta','tiktok','snap','google']:
    md = maxdate_list(D[p]); rows.append((f"D.{p}", md))
    dd = dup_dates(D[p])
    if dd: fail(f"D.{p} has DUPLICATE dates: {dd}")

# GRANULAR inner stores
g_meta_ads   = brace_after('ads:{')            # first ads:{ after meta:{ — handled below precisely
# precise: locate meta:{ then its ads:/adsets:
gi = C.index('meta:{', C.index('const GRANULAR'))
def inner(region_start, token):
    k = C.index(token, region_start); i = C.index('{', k); depth=0; j=i
    while j<len(C):
        if C[j]=='{':depth+=1
        elif C[j]=='}':
            depth-=1
            if depth==0:break
        j+=1
    return json.loads(C[i:j+1])
meta_ads    = inner(gi,'ads:{')
meta_adsets = inner(gi,'adsets:{')
ti = C.index('tiktok:{', C.index('const GRANULAR'))
tt_ads    = inner(ti,'ads:{')
tt_adsets = inner(ti,'adsets:{')
si_ = C.index('snap:{', C.index('const GRANULAR'))
snap_adsets = inner(si_,'adsets:{')
gg = C.index('google:{', C.index('const GRANULAR'))
goog_camps = inner(gg,'campaigns:{')

def store_latest_anyentry(store):
    """max date across all series in an {key:[{d..}]} store."""
    mx=None
    for k,series in store.items():
        for e in series:
            if not dkey(e['d']): continue
            if mx is None or dkey(e['d'])>dkey(mx): mx=e['d']
    return mx

rows.append(("GRANULAR.meta.ads (any ad ran)", store_latest_anyentry(meta_ads)))
# active adset buckets that should be current:
ACTIVE_BUCKETS = ['UAE ALL - ASC','KSA ALL - ASC','KU ALL - ASC','UK ALL - ASC',
                  'Catalogue Retargeting / Prospecting - GCC','Catalogue Adv+ - GCC','Followers GCC - Brand']
for b in ACTIVE_BUCKETS:
    if b in meta_adsets:
        md = maxdate_list(meta_adsets[b]); rows.append((f"  adset «{b[:28]}»", md))
        dd = dup_dates(meta_adsets[b])
        if dd: fail(f"meta.adsets «{b}» DUP dates {dd}")
    else:
        warn(f"meta.adsets missing bucket «{b}»")
rows.append(("GRANULAR.tiktok.ads (any ad ran)", store_latest_anyentry(tt_ads)))
rows.append(("GRANULAR.tiktok.adsets", store_latest_anyentry(tt_adsets)))
rows.append(("GRANULAR.snap.adsets (budget trend)", store_latest_anyentry(snap_adsets)))
rows.append(("GRANULAR.google.campaigns", max((max((d['d'] for d in c['days'] if dkey(d['d'])),key=dkey) for c in goog_camps.values()),key=dkey)))

# standalone const stores
SNAP_SPLIT = brace_obj(r'const SNAP_GEO_SPLIT_DAILY\s*=\s*')
def snap_split_latest(s):
    mx=None
    for geo,ads in s.items():
        for dn,days in ads.items():
            for day in days:
                if not dkey(day): continue
                if mx is None or dkey(day)>dkey(mx): mx=day
    return mx
rows.append(("SNAP_GEO_SPLIT_DAILY", snap_split_latest(SNAP_SPLIT)))

KU = brace_obj(r'const META_KU_COUNTRY\s*=\s*')
rows.append(("META_KU_COUNTRY", maxdate_list(KU) if isinstance(KU,list) else max([k for k in KU if dkey(k)],key=dkey)))

FOLL = brace_obj(r'const META_FOLLOWER_ADS\s*=\s*')
def foll_latest(o):
    mx=None
    for geo,ads in o.items():
        for nm,series in ads.items():
            for dt in series:
                if not dkey(dt): continue
                if mx is None or dkey(dt)>dkey(mx): mx=dt
    return mx
rows.append(("META_FOLLOWER_ADS  *(per-ad rows)*", foll_latest(FOLL)))

for name, md in rows:
    flag = '' if md == LATEST else '  <<< STALE' if md else '  <<< EMPTY'
    if md != LATEST and not name.startswith('  adset') and 'ads (any' not in name:
        fail(f"{name.strip()} latest={md}, expected {LATEST}")
    elif md != LATEST and ('ads (any' in name):
        warn(f"{name.strip()} latest={md} (ok only if no ad ran on {LATEST})")
    print(f"  {name:42s} {str(md):8s}{flag}")

# ============ 2. RECONCILIATION on LATEST day ============
print("\n== RECONCILIATION (latest day) ==")
def geosum(rec, keys, fld):
    return sum(rec.get(k,{}).get(fld,0) for k in keys if isinstance(rec.get(k),dict))
GEOS = {'meta':['uae','ksa','ku','uk','cat','catadv','foll'],
        'tiktok':['uae','ksa','ku','cat'],
        'snap':['uae','ksa','ku'],
        'google':['uae','ksa','ku','cat']}
TOL = {'meta':0.10,'tiktok':0.12,'snap':0.05,'google':0.05}
for p,keys in GEOS.items():
    rec = next((e for e in D[p] if e['d']==LATEST), None)
    if not rec: fail(f"D.{p} has no {LATEST} record"); continue
    gs = geosum(rec, keys, 'spend'); diff = abs(gs - rec['spend'])
    ok = diff <= max(TOL[p], rec['spend']*0.002)
    print(f"  {p:7s} geo-spend Σ={gs:9.2f} vs account {rec['spend']:9.2f}  Δ={diff:5.2f}  {'OK' if ok else 'FAIL'}")
    if not ok: fail(f"D.{p} {LATEST} geo spend Σ {gs:.2f} != account {rec['spend']:.2f}")

# Followers per-ad  ==  adset Followers geo block (overlap dates)
print("\n== FOLLOWERS per-ad ⟷ country block ==")
fb = meta_adsets.get('Followers GCC - Brand', [])
fb_by_date = {e['d']: e.get('geo',{}) for e in fb}
GEOMAP = {'uae':'uae','ksa':'ksa','ku':'ku','uk':'uk'}
checked = 0
for dt in sorted({dt for ads in FOLL.values() for nm,series in ads.items() for dt in series if dkey(dt)}, key=dkey)[-5:]:
    for geo in ['uae','ksa','ku','uk']:
        psum = sum(FOLL.get(geo,{}).get(nm,{}).get(dt,[0,0])[0] for nm in FOLL.get(geo,{}))
        plc  = sum(FOLL.get(geo,{}).get(nm,{}).get(dt,[0,0])[1] for nm in FOLL.get(geo,{}))
        block = fb_by_date.get(dt,{}).get(geo)
        if block is None and psum==0: continue
        if block is None: continue
        if abs(psum-block.get('spend',0))>0.02 or abs(plc-block.get('lc',0))>1:
            fail(f"Followers {dt}/{geo}: per-ad ({psum:.2f},{plc}) != block ({block.get('spend')},{block.get('lc')})")
        else: checked += 1
print(f"  reconciled {checked} geo-day followers cells (last 5 dates)")

# Meta active-adset sum  ==  D.meta.spend  on LATEST
asum = 0
for b in ACTIVE_BUCKETS:
    rec = next((e for e in meta_adsets.get(b,[]) if e['d']==LATEST), None)
    if rec: asum += rec['spend']
md = next(e for e in D['meta'] if e['d']==LATEST)
print(f"\n  meta active-adset Σ={asum:.2f} vs D.meta.spend {md['spend']:.2f}  Δ={abs(asum-md['spend']):.2f}  {'OK' if abs(asum-md['spend'])<0.10 else 'CHECK'}")
if abs(asum-md['spend'])>0.10: warn(f"meta active-adset sum off by {abs(asum-md['spend']):.2f} (may indicate a paused-bucket boundary)")

# ============ 3. STATUS MAPS sanity ============
print("\n== STATUS MAPS ==")
for nm in ['META_AD_STATUS','TIKTOK_AD_STATUS','SNAP_AD_STATUS']:
    M = brace_obj(r'const '+nm+r'\s*=\s*')
    na = sum(1 for v in M.values() if v=='active'); n = len(M)
    bad = [k for k,v in M.items() if v not in ('active','inactive')]
    print(f"  {nm:18s} {na} active / {n} total")
    if na==0: fail(f"{nm} has ZERO active ads — almost certainly broken")
    if bad: fail(f"{nm} has invalid values: {bad[:3]}")

# ---- SNAP_GEO_ACTIVE present, non-empty, and a subset of the split's ads per geo ----
sga=brace_obj(r'const SNAP_GEO_ACTIVE\s*=\s*')
if sga is None:
    fail("SNAP_GEO_ACTIVE missing — Snap ADS panel will not filter to active ads")
else:
    split_nums={g:{re.match(r'^(\d+)',dn).group(1) for dn in SNAP_SPLIT.get(g,{}) if re.match(r'^(\d+)',dn)} for g in SNAP_SPLIT}
    for g,nums in sga.items():
        if not nums: warn(f"SNAP_GEO_ACTIVE[{g}] is empty")
        stray=[n for n in nums if n not in split_nums.get(g,set())]
        if stray: warn(f"SNAP_GEO_ACTIVE[{g}] lists ads not in the split: {stray}")
    print(f"\n== SNAP_GEO_ACTIVE ==\n  " + " | ".join(f"{g}:{len(n)}" for g,n in sga.items()))

# ---- verdict ----
print("\n" + "="*60)
if FAILS:
    print(f"RESULT: ❌ FAIL ({len(FAILS)}) — DO NOT DELIVER")
    for f in FAILS: print("  ✗ "+f)
else:
    print("RESULT: ✅ PASS — safe to deliver")
if WARNS:
    print(f"\nwarnings ({len(WARNS)}):")
    for w in WARNS: print("  ! "+w)
sys.exit(1 if FAILS else 0)
