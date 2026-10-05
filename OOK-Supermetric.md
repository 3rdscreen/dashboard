---
name: ook-report
description: >
  Full workflow skill for updating the One of a Kin (OOK) ad performance dashboard (index.html).
  Use this skill whenever the user uploads ad export files (Meta CSV, TikTok XLSX, Snap XLSX,
  Google CSV) and asks to update the OOK report, add a new day's data, insert daily ad
  performance, or update the dashboard. Also triggers on: "update the report", "add data for
  [date]", "process today's files", uploads of platform exports alongside index.html.
---

# OOK-Supermetric.md — OOK Ad Report Master Skill (Updated Jul 27 2026 — Jul 27 ingest; added RULE 33 (TIKTOK ON = STATUS "Active" — read the TikTok Status column via `ad_opt_status`: ENABLE=Active/ON, DISABLE=Paused/OFF; do NOT use `ad_status` (that's the delivery state AD_STATUS_DELIVERY_OK, a different thing); pull ad_name,ad_opt_status,cost_usd over last_7_days and set active = ad_opt_status==ENABLE; `ad_opt_status` can still lag a very-recent pause so RULE 31 dark-vs-siblings + the user screenshot remain the tiebreak) and RULE 32 (META ON = DELIVERY "Active" OR "Learning" — read the Meta Delivery column as on/off ground truth, treat both Active AND Learning as ON so newly-launched/learning ads aren't dropped; pull the status field with NO status filter and classify on = delivery in {Active, Learning, Learning limited}; and sweep the WHOLE latest-day roster for the RULE 31 dark-vs-siblings pause signal, not just the one ad a fix started from — the Jul 26 487/UAE miss came from flipping only 397/KU when both went dark the same days. Jul 27 app: user said remove 325, it's off / 0 purchases — adstatus showed 325/KU ACTIVE but Delivery was off → flipped inactive, Meta active 23→22, display-only Δ=0.00). Jul 27 structure: AI-177 creative expanded UAE→all 3 geos (named without the "AI | " prefix in KSA/KU), Meta 556+562 launched in KU (Meta active peaked 23), 325/KSA + 227/KU paused-but-spent; TikTok 227 launched KSA; Snap new creative 483 (KSA) + 227 delivering (KU), 487/KU + 556/KSA paused-but-spent. Prior: Jul 17 2026 — Jul 16 ingest; added RULE 31 (STATUS FLAGS GO STALE — the user's Ads Manager screenshot outranks every API. Meta `adstatus` is status AS OF PULL TIME not per-date, so a morning status map goes stale if the client pauses mid-day; and TikTok's management API + `ad_opt_status` BOTH reported ENABLED for an ad the user had already paused. Verify a reported live/off mismatch with TODAY'S DELIVERY — an ad at $0 spend / 0 impressions while siblings in its ad group spend is paused — then flip only that (num,geo) and re-pull the full roster). RULE 24 amended → 24a (mgmt API NOT infallible) and de-duplicated vs 24b. Jul 16 structure: new Meta creative 561 (KSA), new TikTok ad 227 (KW/QA/BH), followers campaign expanded UK-only → 4 geos (ads 177 & 522; its 1 ATC closes Meta's account total). IG follows confirmed NOT available via Supermetrics FA. Prior: Jul 15 2026 — Jul 13 & 14 ingests; added RULE 30 (HIDE-WHEN-EMPTY, NEVER DELETE: a market that goes dark — UK from Jul 14, Catalogue_GCC_ADV+ since Jun 25 — is hidden only for ranges with no data, never deleted, so picking Jul 1–9 brings UK straight back; one shared hasRangeData predicate .filter()-ed onto ALL 7 gr builders, filter AFTER .map() to keep GC[i] colours; corollary: rename DISPLAY labels only, never the data key). Followers campaign renamed GCC Markets → ALL Markets. Jul 14 structure: 2 new Meta creatives (325 new_Spring0325 SS, 547_Minimeabaya0526 SS), Meta UK off, 3 Meta ads paused-but-spending, Snap 547 live in KU/KSA + 489 paused there (SNAP_GEO_ACTIVE now differs per geo). Prior: Jul 13 2026 — Jul 11 & 12 ingests (settled Sale_40%); tightened RULE 28 with the Snap number-collision fix: a distinct Sale display name is NOT enough because buildSnapAdsHTML filters SNAP_GEO_SPLIT_DAILY by ad NUMBER — a retired entry sharing the number (487 in KSA) renders alongside the Sale one → delete the retired split entry (caught by user screenshot: KSA showed 5 ads not 4). Prior: Jul 11 2026 — Jul 5–10 ingests + the Sale_40% cutover across Meta/TikTok/Snap; added RULE 26 (paused-adset residual conversions → use the adset-level geo breakdown, no cost filter), RULE 27 (a new adset can sit at $0 for days before delivering — flip status only on cost>0), RULE 28 (Sale_40% cutover naming + where each platform puts it; TikTok Sale is a NEW campaign), RULE 29 (phantom-active via isAdActive number/EN_ prefix fallback → dash rows; sweep + mark inactive). New catalogue creative EN_Kids. Prior: Jun 19 2026 — Jun 18 ingest delivered; pre-delivery account-level verify caught + fixed a Google PMAX_KSA restate-down (conv 9→8); added RULE 20: Meta Catalogue is now TWO campaigns — Catalogue_GCC + Catalogue_GCC_ADV+, split across THREE data stores (adsets/ads/geo) + all 5 views, never re-merge; RULE 21: Google "Budget Shift Detection" widget hidden; snap.ads dup confirmed vestigial/non-breaking and left as-is. Prior Jun 18: RULE 17 JS duplicate-key trap; RULE 18 SNAP_GEO_SPLIT_DAILY authoritative; RULE 19 Google days newest-first; paths → ook.html)

## Overview
Single-file HTML/JS dashboard tracking Meta, TikTok, Snap, Google across GCC markets.

**File:** `ook.html` → `https://3rdscreen.github.io/dashboard/ook.html`  
**Source (read-only):** `/mnt/project/ook.html`  
**Working path:** `/home/claude/work.html` (copy source here; never edit source directly)  
**Output:** `/mnt/user-data/outputs/ook.html` (ALWAYS — never `index.html`)  
**Delivery sequence:** `cp work.html /mnt/user-data/outputs/ook.html` → `present_files`  
**Data objects:** `const D={...}` (daily platform totals) · `const GRANULAR={...}` (ad/adset level)

---

## ═══ CURRENT CAMPAIGN STATE (as of Aug 23 2026 ingest) ═══
**MAJOR CUTOVER Aug 10 2026: "Sale 40%" → new "Prospecting" phase, across ALL THREE ad platforms.** The old Sale-40% ads (227, 397, 483, 487, 489, 499, 527, 530, 543, 556, 559, 561-Newcolor, and the 227/397/487/530/556/527 FINAL HOURS variants) are ALL PAUSED/inactive now. The new active creative set is **560, 561, 562, 563, 564** in all three GCC geos (UAE / KSA / KW-QA-BH):
- `560_KidsAbaya0726_Fm_Vid short_Vert_Details_En_GLO`
- `561_KidsAbaya0726_Fm_Vid short_Vert_Transitions VO_En_GLO`
- `562_KidsAbaya0726_Fm_Vid short_Vert_Transitions _En_GLO` (note the space before `_En`)
- `563_UGC26_Wm_Vid short_Vert_UGC_En`
- `564_UGC26_Mn_Vid short_Vert_UGC VO_En`

**TikTok:** campaign `GCC | Sales | Prospecting` (id `1870266496222258`, unchanged id, renamed). ACTIVE adgroups = `UAE | Prospecting | July 2026` (1873142526030882), `KW/QA/BH | Prospecting | July 2026` (1873142526029138), `KSA | Prospecting | July 2026` (1873142526025058) — each holds 560-564 ENABLED. The three `… | Sale 40% | July 2026` adgroups are **status PAUSED** (their ads still show ENABLED — RULE 38: adgroup paused ⇒ every ad in it is inactive regardless). tiktok.ads keys `<full 560-564 name>_Tiktok_<UAE|KSA|Ku/Qa/BH>_Sale`; all old Sale ad keys set inactive. 560-564 with 0 delivery in a geo but ENABLED ⇒ seed active-with-zero (RULE 38 new-ad case).

**Snap:** active squads = `KSA - Retargeting - May 2026`, `KW/QA/BH - Retargeting - May 2026`, `UAE - Retargeting - Apr 2026` (all "(7-Day Att)"). `SNAP_GEO_ACTIVE = {UAE,KSA,"KU / QA / BH"} → all ["560","561","562","563","564"]`. Old `… - Sale 40%- July 2026 (7-Day Att)` squads are PAUSED. 560-564 first delivered on Snap Aug 10 (zero before). split/snap.ads keys use the full name + `[<GEO> Sale]` / `_Snap_<geo>_Sale`.

**Meta:** ACTIVE adsets = `UAE_ALL-ongoing-Prospecting-ASC_EN-MAR26`, `KSA_…MAR26`, `KUW-QAT-BH_…MAR26` (ads 560-564, keyed `<name>_Meta_<UAE|KSA|Ku&Qat>_Sales_ASC`) + catalogue adset `GCC_Retargeting & Prospecting - catalogue` with exactly 5 ads: `EN_Kids_Abaya…Catalogue` (NEW), `EN_Plus Size-page_catalogue_Static-Carousel`, `EN_All…Catalogue`, `EN_Women…Catalogue`, `EN_Men…Catalogue`. The `…Sales_40% | JUL2026` adsets are OFF — so the Aug-10 holdovers I briefly kept active (397, 489, 556, 561-Newcolor) are now INACTIVE. META_AD_STATUS active set = those 15 MAR26 ad keys + those 5 exact catalogue keys, nothing else. Catalogue export names may appear as `…catalog…` (no -ue / no `_Catalogue` suffix) on some days — map to the existing `…catalogue…Catalogue` store keys.

**Meta followers:** GCC followers are now a single ad `Reel | 10 Aug 2026` per geo (replaced the old 177 + 522 split from Aug 10); UK still `415_Terra0825…` + `418_Terra0825…`. `META_FOLLOWER_ADS` must carry the Reel ad + geo lc so per-ad Σ == the followers block.

**Google:** new campaign `PMAX_KSA_Pyjama_AR_goog` (KSA geo) started ~Aug 10 alongside `PMAX_KSA_Pyjama_EN_goog`.

### ★ Aug 14 2026 creative refresh — new ads added on top of 560-564
On Aug 14 three new creatives launched into the same active adsets/adgroups (all started $0-conversion; they've since begun converting):
- **566** `566_BeatTheHeat_All_Static_Vert_Details_En` — **Meta only** (MAR26 adsets, all 3 geos).
- **567** `567_Mask1225_BeatTheHeat_Cp_Vid short_Vert_Details VO_En` — **Meta + TikTok + Snap**. (TikTok KSA key is a `Copy 1 of …` variant but stores under the normal 567 KSA key.)
- **568** `568_Ounass2026_All_Vid short_Vert_Details VO_En` — **Snap only**, UAE squad only.

Current active sets (as of Aug 16):
- **TikTok:** `560,561,562,563,564,567` — all ENABLED in all 3 Prospecting adgroups (roster-confirmed). 18 active tiktok.ads keys (6 ads × 3 geos).
- **Snap:** SNAP_GEO_ACTIVE is now **geo-specific** (per-ad pauses in play): `UAE = [560,562,564,567,568]`, `KSA = [560,561,562,563,564]`, `KU / QA / BH = [560,561,562,564,567]`. (561 paused in UAE; 563 paused in UAE+KU; 567 not run in KSA; 568 UAE-only.)
- **Meta:** per-geo active (20 ad keys + 5 catalogue). Active `(num→geos)`: 560 all3, 561 KSA+KUW only, 562 UAE only, 564 all3, 566 all3, 567 all3, **563 fully paused on Meta** (still live on TikTok/Snap). Build META_AD_STATUS from the exact `(ad,geo)` ACTIVE/PAUSED rows of the status pull — no longer a flat "all geos" list.

**RULE (per-geo status, all platforms):** ad status is now resolved per `(number, geo)`, not per number. A creative can be ACTIVE in one geo and PAUSED in another on the same platform. Always rebuild STATUS/`SNAP_GEO_ACTIVE` from the latest live status pull's exact ad+geo (Snap: ad+squad+campaign all ON) rows.

**TikTok adgroup rename:** the three Prospecting adgroups were renamed `… | Prospecting | July 2026` → `… | Prospecting | Aug 2026` (~Aug 14). **Same adgroup IDs, same ads** (UAE 1873142526030882 / KW-QA-BH 1873142526029138 / KSA 1873142526025058) — cosmetic only, no ingest impact. The three Sale 40% adgroups remain PAUSED.

### ★ Aug 17 2026 second creative wave — BeatTheHeat26 (569, 571, 572, 573, 574)
A second wave launched Aug 17 (all $0-conversion day one, since converting):
- **569** `569_BeatTheHeat26_Mn_Vid short_Vert_Details VO_En` — Meta + TikTok + Snap.
- **571** `571_BeatTheHeat26_Mn_Vid short_Vert_Transitions VO_En` — **Meta KSA** only.
- **572** `572_BeatTheHeat26_Wm_Vid short_Vert_UGC VO_En` — Meta (UAE) + TikTok (**KW/QA/BH only**) + Snap (all geos).
- **573** `573_BeatTheHeat26_Wm_Vid short_Vert_Details VO_En` — **Meta KUW** only.
- **574** `574_BeatTheHeat26_Cp_Vid short_Vert_Details VO_En` — Meta + TikTok + Snap. (TikTok/Snap KSA are `Copy 1 of 574` variants but store under the normal 574 KSA key.)

### ★★★ STANDING RULE — RECONCILE THE SHOWN-AD SET ON EVERY UPDATE (all platforms, all geos) [user instruction, Aug 24 2026]
**Run this every ingest, proactively, without being asked.** After building the day's data, fully reconcile which ads render as active on **all four platforms and every geo**: **remove every OFF/inactive ad and add every ON/active ad that is currently hidden**, resolved per `(ad, geo)`. Geo/adset/D totals already contain all spend (paused ads, new ads, everything), so this only changes which per-ad rows render — **ties are unaffected**. When a newly-active ad is added to the shown set, also add its per-ad rows to the platform's `.ads` block so it actually renders.
- **Meta & Snap:** rebuild the STATUS maps (`META_AD_STATUS`, `SNAP_GEO_ACTIVE`/`SNAP_AD_STATUS`) from the live **ACTIVE** status pull (already standard each ingest — keep doing it).
- **TikTok:** see the method + API-lag warning immediately below.
- **Precedence:** a user's Ads Manager **Status** screenshot always overrides these heuristics. **Flag borderline ads** (dark only 1–2 days) so the user can restore them with a word.

### ★★ TikTok ACTIVE/INACTIVE — NO API OR DELIVERY SOURCE WORKS; ONLY IBRA'S SCREENSHOT [RULE 39, updated Sep 1 2026 — supersedes the delivery method + RULE 33/34]
TikTok Ads Manager has a per-ad **Status** column (**ON = Active / OFF = Paused**) that is the true ground truth, resolved per `(ad, geo)`. **Ibra has flagged repeatedly that I keep getting this wrong. The reason: NOTHING in any data feed reflects his real on/off toggle — not the reporting API, not the Management API, and NOT delivery.** Confirmed by direct test **Sep 1 2026** on the `KW/QA/BH | Prospecting | Aug 2026` ad group:
- Reporting `ad_status` → `AD_STATUS_DELIVERY_OK` for **every** ad, incl. 560/561/563/567/568/572/574 which had **$0 spend and were OFF** in his UI.
- Reporting `ad_opt_status` → `ENABLE` for all (same as Aug 23).
- Management API `campaign_and_resource_get` (`campaign_detail_level: ad`) → `status: ENABLED` for **every** ad in an enabled ad group, incl. the clearly-off ones.
- **Delivery is ALSO not a proxy:** 569 and 571 both logged spend on Aug 31 ($22.82, $49.24) yet Ibra had them **OFF**. So the old "spent >$1 in last 2 days = active" heuristic is WRONG and is exactly what kept resurrecting ads he'd paused.

**So the delivery method below is RETIRED, and RULE 33 (`ad_opt_status`) / RULE 34 roster-seeding for on/off are NOT reliable.** The ONLY authority for TikTok per-ad on/off is **Ibra's Ads Manager screenshot / list.**

**Method (do this, nothing else):**
1. **Carry forward** the LAST IBRA-CONFIRMED active set per geo across ingests — do NOT recompute it from delivery or any status field each session.
2. **Only change a geo's active set when Ibra gives a screenshot/list for that geo.** When he does, set **exactly** that set `active` for that geo and **everything else in that geo `inactive`** — no additions from delivery.
3. When a **new creative** appears in the reporting pull (e.g. 575), still **add its per-ad `tiktok.ads` rows + geo/adset/D data** so it *can* render, but leave it `inactive` until Ibra confirms it's on (or he's already listed it).
4. **Ad-GROUP status IS reliable from the Management API** — the three `… | Prospecting | Aug 2026` groups are ENABLED; the `… | Sale 40% | July 2026` groups are PAUSED (all their ads inactive regardless). Use that only to know which ad *groups* are live, not which ads.
5. Geo/adset/D totals already include ALL spend, so status only changes which rows *render* — ties are never affected.

**Live campaign (Sep 1 2026):** `GCC | Sales | Prospecting` = **`1870266496222258`** (ENABLED). The old `1831579436999697` ("GCC - Sales (prospecting)") is now **PAUSED** — don't pull ad status from it. Live ad groups: `UAE|Prospecting|Aug 2026` (1873142526030882), `KW/QA/BH|Prospecting|Aug 2026` (1873142526029138), `KSA|Prospecting|Aug 2026` (1873142526025058).

**Last Ibra-confirmed TikTok active sets:** UAE — 567 OFF (Sep 1); KW/QA/BH — **{564, 570, 573, 575}** exactly (Sep 1 screenshot). KSA + the rest of UAE still pending his confirmation (currently carried from the old heuristic — ask him).

**Current TikTok active sets (delivery-reconciled Aug 24 2026, combo retired, 568/573 added):**
- **UAE (5):** 561, 563, 567, 568, 574
- **KSA (5):** 561, 564, 568, 573, 574
- **KW/QA/BH (5):** 561, 563, 568, 569, 572
Combo – 20 Aug wave: **retired** (all 6 captions dark since Aug 22). Borderline dropped for zero recent delivery — 574/KU, 569/UAE, 560 (all), 563/567 KSA — restore on user word.

### ★ Meta Overview ROAS excludes Followers spend (renderer rule, user instruction Aug 17)
In the **Overview** only, **Meta** ROAS = `SV ÷ (Meta total spend − Followers spend)` — the brand/traffic Followers budget earns no purchase revenue, so it's removed from the ROAS denominator. Implemented in all three overview renderers (`renderOverview` single-day, `renderOverviewRange`, `renderOverviewMTD`) via a per-platform `roasSpend` accumulator that subtracts `r.foll.spend` when `p.key==='meta'`; the blended total uses `totSV / Σ roasSpend`. The **Spend** figure still shows full Meta spend (incl. followers) — only ROAS changes. TikTok/Snap/Google unchanged. (Aug MTD effect: 3.25× → 3.42×.) Do not revert this when editing overview aggregation.

**Coverage:** daily ingest complete through **Aug 23 2026**; July fully reconciled.

---

## ═══════════════════════════════════════
## NON-NEGOTIABLE RULES — READ EVERY TIME
## ═══════════════════════════════════════

### RULE 1 — NEVER FABRICATE DATA
- Only insert numbers from actual uploaded export files
- New ads: data ONLY from the day they first appear in an export
- Spend-only entries (sv=0, conv=0, atc=0, roas=0, cpo=0) are acceptable when no conv data exists
- **NEVER** proportionally distribute sv/conv/roas/atc/cpo from D object totals
- **NEVER** invent ATC, conv, or SV — these must come from the export

### RULE 2 — SPEND MUST ALWAYS MATCH THE UPLOADED EXPORT EXACTLY
**This is non-negotiable.** Ibra has explicitly emphasized: the spend in the uploaded document must equal the spend in the dashboard to the cent.

For every day being inserted or updated, compute per-platform totals from the export and verify:
```python
# Meta (already USD)
meta_spend = m[m['Amount spent (USD)'] > 0]['Amount spent (USD)'].sum()  # all rows, sales + followers

# TikTok (AED → USD)
tt_spend = tt[tt['Primary status']=='Active']['Cost'].sum() / 3.67

# Snap (USD already)
snap_spend = snap['Amount Spent'].sum()

# Google (AED → USD, filter Campaign status == 'Enabled' to exclude total rows)
g_spend = g[g['Campaign status']=='Enabled']['Cost_clean'].sum() / 3.67
```
Then validate the D object's new `"Apr N"` entry has `spend` matching these values. If off by even a cent, stop and fix.

Also validate the sum of per-geo spends equals the top-level total, and sum of per-ad spends in GRANULAR equals the top-level total.

TikTok UAE spend has been wrong on multiple dates — always recompute from export, never trust stored geo values.

### RULE 3 — JSON PARSE + RE-SERIALIZE FOR D OBJECT EDITS
```python
d_start = content.find('const D={')
i = d_start + len('const D=')
# brace-count to find d_end
d_obj = json.loads(content[i:d_end])
# modify d_obj entries
new_d = json.dumps(d_obj, separators=(',',':'))
content = content[:i] + new_d + content[d_end:]
```
Never use string replacement for D object multi-field edits — format uncertainty causes silent failures.

### RULE 4 — PLATFORM STATUS MAPS ARE FULLY INDEPENDENT
- `TIKTOK_AD_STATUS` → built from TikTok export `Primary status` column ONLY
- `SNAP_AD_STATUS` → built from Snap export ONLY
- `META_AD_STATUS` → built from Meta export ONLY
- **NEVER cross-use.** isTTAdActive must never check Meta/Snap status.

### RULE 5 — NO DUPLICATE JS VARIABLE DECLARATIONS
Before adding ANY `const`/`let` to a JS function, scan the **entire function** for existing declarations of the same name. Duplicate `const` = `Uncaught SyntaxError` = entire dashboard broken. Common collisions: `const last`, `const ds`, `const p`, `const i`.

### RULE 6 — CACHE MUST RESET ON EVERY RENDER
`buildTTAdsHTML` and `buildSnapAdsHTML` must start with:
```js
window.TT_AD_DAILY_CACHE = {};    // in buildTTAdsHTML
window.SNAP_AD_DAILY_CACHE = {};  // in buildSnapAdsHTML
```
Without reset, switching periods (e.g. all-time → last 7 days) leaves stale data in cache, causing hover to show wrong numbers (e.g. 37 sales vs table's 24).

### RULE 7 — HOVER CACHE FROM BREAKDOWN dayAgg ONLY
- `TT_AD_DAILY_CACHE` and `SNAP_AD_DAILY_CACHE` populated inside the breakdown day loop from `dayAgg`
- Same source as the table = hover always matches table
- Also populate in fallback else-branch (when breakdown hidden) using same dayRecs logic
- `getAdDailyData` fallback reads ALL-TIME data — cache must be hit to avoid wrong totals

### RULE 8 — ALWAYS CHECK LAST LINE + JSON VALIDITY
```python
json.loads(content[i:d_end])                          # D object valid ✓
assert content.splitlines()[-1].strip() == '</html>'  # no corruption ✓
```
Use `content.rfind('</script>')` not `find()` — Chart.js CDN tag creates an earlier match.

### RULE 9 — META AD-LEVEL RENDER TRIPLET (new ALL buckets)

When a geo migrates from split (Abaya/Pyjama) to consolidated (ALL) — UAE Apr 27, KU Apr 28, KSA May 7 — **three lines in the Meta ad-level renderer must be updated together**. They are a coupled triplet: the input classifier, the output bucket order, and the day-row filter. Updating one without the others silently hides the geo's data, because data goes into a bucket nobody reads from.

**The three lines (verified May 8 2026):**

| Line | Role | Pattern |
|---|---|---|
| ~1629 | Input: classify ad → `ct` | `const ct = (geo==='Catalogue') ? 'Catalogue' : (geo==='UAE'\|\|geo==='KSA'\|\|geo==='KU / QA / BH') ? 'ALL' : detectCampType(name);` |
| ~1681 | Output: which CT buckets to render per geo | `const campOrder = g.label==='Catalogue' ? ['Catalogue'] : (g.label==='UAE'\|\|g.label==='KSA'\|\|g.label==='KU / QA / BH') ? ['ALL'] : ['Abaya','Pyjama','Catalogue'];` |
| ~1713 | Day breakdown: match ads to day rows | `const nameCT=(adGeo==='Catalogue')?'Catalogue':(adGeo==='UAE'\|\|adGeo==='KSA'\|\|adGeo==='KU / QA / BH')?'ALL':detectCampType(name);` |

All three must list **the same set** of geos in the ALL branch. Any drift = entire geo section disappears from the Ad-level view.

**Failure symptom:** An entire geo (KSA, KU/QA/BH, etc.) is missing from the Meta Ad-level view, even though its data exists in `D.meta.<geo>` and `GRANULAR.meta.adsets["<GEO> ALL - ASC"]`. Cause: line 1629 marks ads with `ct='ALL'` but line 1681's `campOrder` still expects `['Abaya','Pyjama']` → `presentTypes=[]` → `geoSpend=0` → `return` → geo skipped.

**Find the triplet quickly:**
```bash
grep -n "geo==='UAE'\|adGeo==='UAE'\|g.label==='UAE'" /home/claude/index.html
# Should return exactly 3 lines, all with the same set of geos in the ALL branch.
```

**Other render references that already include ALL keys (verify after each migration but don't usually need editing):**
- `META_CAMPS` array (~line 3721) — drill-down config; lists both new and legacy keys
- `aggMetaGeo([...])` calls in metaAdsets (~line 1952, ~line 2103) — already aggregate new + legacy
- Budget Trend chart (~lines 2797-2801) — historical Abaya/Pyjama lines kept for trend continuity (do NOT remove)

### RULE 10 — ACCOUNT-LEVEL RECONCILIATION (catches attribution drift)

Per-ad-sum reconciliation only proves arithmetic — that my pull adds up to itself. It does NOT prove the data is current. Between two pulls of the same date, platforms (especially Google and TikTok) re-attribute conversions and SV; late impressions trickle in for Meta. Without a second cross-check, drift between pulls is invisible until the user spot-checks against Ads Manager.

**Mandatory check before delivery: fire one extra account-level query per platform on TARGET, assert per-ad/per-campaign sum matches account-level total within tolerance.**

```python
# Account-level pull (one row per platform per day)
TOL_SPEND = 5.0     # USD
TOL_CONV  = 1       # absolute
TOL_ATC   = 5       # absolute (Snap commonly has 4-6 unattributed)

# For each platform: pull date-only totals, compare to per-ad sum.
# Meta:    fields=date,cost,offsite_conversions_fb_pixel_purchase,offsite_conversion_value_fb_pixel_purchase,offsite_conversions_fb_pixel_add_to_cart,currency
# TikTok:  fields=date,advertiser_currency,cost,cost_usd,complete_payment,total_complete_payment_rate,web_event_add_to_cart
# Snap:    fields=date,spend,conversion_purchases,conversion_purchases_value,conversion_add_cart,currency
#          (+settings={"action_report_time":"impression","attribution_window":"1_DAY__7_DAY"})
#          (NOTE: from May 14 2026 onward all Snap squads are on 7-day click attribution.
#           Before May 14, only the UAE squad was on 7-day while KSA + KU were on 28-day,
#           but the file pulled May 1-13 with 1_DAY__28_DAY so historical UAE numbers in the
#           file slightly differ from the platform's 7-day truth (~$674 SV net understated
#           over 13 days). Do NOT retroactively repatch — the file represents the pull-time
#           snapshot. From May 14 ingest, use 1_DAY__7_DAY.)
# Google:  fields=Date,Cost,Cost_usd,Conversions,ConversionValue,Currencycode

assert abs(account_spend_usd - my_per_ad_sum_usd) < TOL_SPEND, "DRIFT: re-pull"
assert abs(account_conv      - my_per_ad_conv)    <= TOL_CONV,  "DRIFT: re-pull"
```

**If drift detected:** re-pull the per-ad/per-campaign data fresh, recompute `D.<plat>.<TARGET>` and patch `GRANULAR` ads/adsets/campaigns for that day. Do NOT just adjust top-level `D.<plat>.spend` to match — the per-ad GRANULAR data must agree.

**Confirmed cases:**
- TikTok Apr 30 — 2 conv re-attributed between pulls (in skill history)
- Google May 8 — `PMAX_UAE_Pyjama_EN_goog` gained 2 conv + $1,021 SV between pulls (~30 min apart)
- Meta May 8 — $0.58 late-impression drift across 6 ads

**Snap ATC tolerance specifically:** Snap ad-level rows commonly sum to 4-6 fewer ATCs than account-level (unattributed events). Allow `TOL_ATC=5` for Snap; do NOT re-pull just for ATC delta in this range.

---

### RULE 11 — BACKFILL DRIFT CHECK (prior-7-day re-pull before every delivery)

RULE 10 catches drift on TARGET day only. But TikTok and Snap have 28-day click attribution windows — conversions land 1-7+ days **after** the impression. A day delivered last week is almost always understated by the time of the next delivery. Without a backfill check, the dashboard chronically reports stale ROAS on every prior day.

**Mandatory check before delivery: re-pull account-level for the past 7 days on every platform, compare to file's existing D entries, patch any drift.**

```python
# Pull all of past 7 days in one query per platform (TARGET-7 to TARGET)
# Same field lists as RULE 10 account-level queries.
# Compare each day's row to D.<plat>[day_idx].
# Drift threshold: any conv delta, OR spend delta > $0.10, OR sv delta > $2.
```

**If drift found on a prior day:** re-pull per-ad/per-campaign for that day (use OR'd date filter for batch efficiency: `date == 2026-05-06 OR date == 2026-05-08 OR ...`) and patch D + GRANULAR ads/adsets/campaigns for that day. Same patch flow as RULE 10.

**Confirmed scale of impact (May 1-13, 2026):**
- TikTok: 4 of 13 days drifted, +8 conv, +$1,934 USD SV recovered (~11% of TT period revenue)
- Snap: 6 of 13 days drifted, +19 conv, +$4,113 USD SV recovered (~7% of Snap period revenue)
- Meta: $0.50-$1.50 late-impression spend drift on most prior days (small, but compounds in 7-day rollups)

**Never assume "delivered = final."** Always backfill.

---

### RULE 12 — PRE-DELIVERY LIVE STATUS CHECK (ad active-state matches platform NOW)

> ⚠️ **See RULE 31 (Jul 17 2026):** status flags are "as of pull time", not per-date, on BOTH Meta and Snap — and TikTok's
> status endpoints (management API included) can lag hours behind a recent pause. A status map built during a morning
> ingest can be stale by afternoon. If the user reports a live/off mismatch, verify with TODAY'S DELIVERY
> (cost/impressions = 0 while siblings in the same ad group spend), never with the status field.

> ⛔ **BLOCKING — the single-day shortcut is the #1 recurring failure of this rule.**
> The status map MUST be rebuilt from a **7-day window pull filtered on `ad_status`**, set as the source of truth.
> NEVER derive the active set from a single-day pull, and NEVER infer "active" from "appeared in today's pull / spent today."
> A single-day insights pull is **delivery-filtered by the platform**: it only returns ads that had impressions that day, so any ad that is genuinely ACTIVE but didn't happen to spend that day is silently dropped → defaults to `inactive` → vanishes from the Active-ads panel. This is the same `cost>0` trap wearing a different mask (a one-day window IS a spend filter). If the script's status query has `start_date == end_date`, it is WRONG — stop and widen to the 7-day window.

The daily export's `ad_status` reflects status during the export window, not current state. An ad that ran all day and was paused at 11pm shows `ACTIVE` in the day's export but is `PAUSED` on the platform now. The dashboard's "Active ads" view must reflect **current platform state**, not "delivered today."

**CRITICAL FIX (the `cost > 0` trap):** A prior version of this rule pulled live status with a `cost > 0` filter and only flipped paused-but-spending ads. This is BROKEN — it can only see ads that spent today. A paused ad with **zero spend today is invisible** to a `cost > 0` pull, so it stays marked `active` in the file forever. This is exactly why stale-active ads (paused Tank ads, dead geo-variants) survived undetected and the user had to catch them from Ads Manager screenshots. **Never derive the active set from a spend-filtered pull.**

**MANDATORY METHOD — per-geo ACTIVE reconciliation (no cost filter):**
For each platform, pull the ads whose **current** status is ACTIVE, scoped per geo/ad-set, then set the file's active set to **exactly** that returned list — nothing more, nothing less. This catches BOTH directions in one shot: stale-active (in file, not on platform) AND missing-active (on platform, not in file).

```python
# Meta — one pull PER GEO (UAE / KSA / KU). Filter on STATUS, not cost:
#   fields=ad_name,ad_set_name,ad_status,cost
#   filter: ad_set_name =@ UAE AND ad_status == ACTIVE      (then KSA, then Ku)
#   date_range_type=last_7_days, compress=true
# TikTok:  fields=ad_name,ad_status,cost_usd     filter: ad_status == AD_STATUS_DELIVERY_OK
# Snap:    fields=ad_name,ad_squad_name,ad_status,spend  filter: ad_status == ACTIVE
# Google:  no ad-level status (campaign-level only)

# Reconcile — the live ACTIVE list IS the truth:
live_active = set(rows_returned_by_status_eq_ACTIVE_pull)   # exclude Followers ad-set ads (user turned off)
for ad in file_status_map:
    file_status_map[ad] = "active" if ad in live_active else "inactive"
# Any live_active ad missing from the map → add it as active.
```

**Exclude Followers ad-set ads** from the active set regardless of platform status — they show ACTIVE and keep spending residually (~$50-110/day) but the user keeps them OFF in the dashboard (standing instruction). Force them inactive.

**Dedupe naming variants BEFORE reconciling:** the same ad can appear under two keys — `Ku_Qa` vs `Ku&Qat`, or single-vs-double-space (`...VO_En_GLO  _Meta` vs `..._En_GLO_Meta`). Use the file's existing key spelling as canonical; delete the stale duplicate rather than carrying conflicting status on two keys. Match on the ad-number prefix + geo, not the full string.

**Why this matters:** "Active ads" view drives the dashboard's most-watched section, and the client compares it directly against their Ads Manager On/Off column. If a paused ad shows there, the user looks bad. The answer to "are the active ads right?" must be "yes, verified per-geo against `ad_status == ACTIVE`" — not "yes, the ones that spent today."

**MANDATORY RULE 12 CHECKLIST — run every session, every platform, before delivery:**

**Step 1 — Pull 7-day active ad list per geo (NOT last-day-only, NOT cost-filtered):**
```python
# Meta: one pull PER geo. date_range_type=last_7_days. NO cost filter. fields=ad_name,ad_set_name,adstatus,cost
#   ⚠️ META ON = DELIVERY IS "Active" OR "Learning" (see RULE 32). Do NOT filter to ACTIVE only — that DROPS
#      ads still in the Learning phase, which ARE on. Pull WITHOUT a status filter and classify in Python:
#      on = delivery_value in {"Active","Learning","Learning limited"}  →  active ; everything else → inactive.
#   UAE: filter: ad_set_name =@ UAE AND campaignobjective != OUTCOME_TRAFFIC
#   KSA: filter: ad_set_name =@ KSA AND campaignobjective != OUTCOME_TRAFFIC
#   KU:  filter: ad_set_name =@ Ku  AND campaignobjective != OUTCOME_TRAFFIC
#   UK:  filter: ad_set_name =@ UK  AND campaignobjective != OUTCOME_TRAFFIC
# TikTok: fields=ad_name,ad_opt_status,cost_usd  →  active = ad_opt_status=="ENABLE" (Status column Active/Paused, RULE 33)  date_range_type=last_7_days
# Snap:   fields=ad_name,ad_squad_name,ad_status,spend  filter: ad_status == ACTIVE  date_range_type=last_7_days
```

**Step 2 — Cross-check BOTH directions:**
- **Stale-active:** in STATUS map as `active` but NOT in platform pull → flip to `inactive`
- **Missing-active:** in platform pull but NOT in STATUS map (or wrong value) → add/flip to `active`
- **New ads:** brand-new ad numbers not in STATUS map at all → add with correct geo-suffixed key
- **Meta (RULE 32):** the platform "pull" = ads whose Delivery is **Active OR Learning**. A Learning ad is ON — never let it fall to `inactive`. Scan EVERY ad on the latest day for the dark-vs-siblings pause signal (RULE 31), not just the one that prompted a fix — the Jul 26 miss (487 UAE dark same days as 397 KU, only 397 flipped) came from checking one ad instead of the whole roster.

**Step 3 — Verify per-geo country breakdown (Meta KU only):**
- Re-pull `date,Countryname,cost` filtered `ad_set_name =@ Ku` for last 7 days
- Confirm KW/QA/BH split is consistent with `META_KU_COUNTRY` block

**Step 4 — Cross-check breakdown data (last 7 days + last 3 days):**
- Pull account-level date-broken-down for all 4 platforms for last 7 days
- Compare each day to `D` object — catch any conv/SV/spend drift (RULE 11 overlap)
- Specifically flag last 3 days as highest maturation-drift risk

**Step 5 — Confirm count matches AM before delivery:**
- State explicitly: "Meta UAE: N active ads / KSA: N / KU: N / UK: N — matches AM ✓"
- If user sends an AM screenshot, count must match exactly. No exceptions.

**Confirmed cases:**
- May 13: `Combo_En_GLO  _Meta_UAE_Sales_ASC` had $683 spend then was paused — export said ACTIVE, platform said PAUSED. Flipped to inactive.
- May 20: stale-active ads invisible to the old `cost > 0` check — 522_Tank UAE + 526_Tank KU (Meta, paused, $0 today) and 5 TikTok geo-variants stayed `active` in file until user flagged from screenshots.
- May 21 verified: Meta UAE 7 / KSA 7 / KU 6 active, all reconciled exactly to user's AM screenshots via per-geo ACTIVE pull.
- Jun 18: `513_Abaya0126_Mn_Vid..._Meta_UAE_Sales_ASC` was correctly ACTIVE but dashboard was missing 4 NEW ads (549/550/552/553 — PlusSizes0626 + new Abaya/Minime) that launched in UAE + KSA + KU. Root cause: new ad numbers had zero STATUS map entries → `isAdActive()` returned false → invisible. Fix: per-geo ACTIVE pull with `last_7_days` (not today-only) caught them immediately. **Every ingest must pull 7-day window to catch ads launched mid-week.**
- Jun 21: client screenshot showed Meta **UAE = 2 active, KSA = 2 active** (527/513 and 527/548) when the true count was **UAE = 6, KSA = 6** (UAE: +549/553/552/550; KSA: +546/552/550/553). Data was fine — all 9 ads/geo had spend in the window. Root cause: the daily-ingest status step had drifted to a **single-day** `ad_status` pull (`start==end`), which Meta delivery-filters, so only the two top-spending ads that delivered on the latest day were returned and marked active; every active-but-not-spending-that-day ad fell to `inactive` and was hidden. Fix: rebuilt all status maps from the 7-day window `ad_status` pull (RULE 12 as written). **The rule was correct; execution had silently reverted to the single-day shortcut. The `start==end` guard above now makes that reversion a hard stop.**

---

### RULE 13 — NEW GEO LAUNCH (wire EVERY render location, not "4 places")

When a brand-new geo bucket is created (e.g. **UK on Meta, May 25 2026** — `UK_ALL-ongoing-Prospecting-ASC_EN-MAY26`, $150/day, Meta-only), adding `D.<plat>.<geo>` + the `GRANULAR.<plat>.adsets["<GEO> ALL - ASC"]` bucket is only the data half. The Meta tab has **multiple INDEPENDENT render paths that each carry their own hardcoded geo list.** Editing one (or "the 4 places" from an old note) leaves the geo invisible in the others. The May 25 UK launch took THREE separate fix passes because each path was discovered only when the user screenshotted what was still missing. **Do all of these in the same session as the data insert.**

**The authoritative checklist — a new Meta geo `<geo>` (key e.g. `uk`, label e.g. `UK`, adset bucket `UK ALL - ASC`) must be added to ALL of:**

| # | Location (~line, re-grep each time) | What to add | Symptom if missed |
|---|---|---|---|
| 1 | **`GK` map** (~line 565) `meta:[...]` | add `"uk"` (Meta only — leave tiktok/snap/google) | **Missing from Market Breakdown MTD / Last 7 / Last 30 / range tables** (this is the big one — all 4 breakdown tables read `GK[pk]`) |
| 2 | **`GL` map** (~line 571) | add `uk:"UK"` label | geo row shows blank/undefined label |
| 3 | **`GC` array** (~line 572) | add a 5th color (e.g. `"#9333ea"` purple) — Meta now has 5 geos; `GC[i]` for index 4 is else `undefined` | geo dot renders with no color |
| 4 | **`metaAdsets` #1** (~line 1885, the `aggMetaGeo` block) | `{ name:'UK Sales - ASC', agg: aggMetaGeo(['UK ALL - ASC']) }` | missing from campaign overview |
| 5 | **`metaAdsets` #2** (~line 2033, the `aggAdset` block) | `{ geo:'UK', agg: aggAdset('meta',['UK ALL - ASC']) }` | missing from adset overview |
| 6 | **`META_CAMPS`** (~line 3656) | `{ label:"UK", adsets:["UK ALL - ASC"], prefix:"UK ·" }` | missing from SALES CAMPAIGNS + AD SETS drill-down tables |
| 7 | **`BUDGET_TREND_CONFIG.meta.series`** (~line 2740) | `{ key:'UK ALL - ASC', label:'UK · ALL', color:'#9333ea', dash:[] }` | missing from budget trend chart |
| 8 | **`GEO_GROUPS2`** in `reRenderMetaAds()` (~line 1535) | `{ label:'UK', pattern:/[_ ]UK$/i }` | **ON ads missing from Ad-level view** (the period-button view); `detectGeo2` returns null → `if(!geo) return` drops every UK ad |
| 9 | **`GEO_GROUPS`** static ADS render (~line 4448) | `{ label:"UK", pattern:/[_ ]UK$/i }` | missing from the static ads table |
| 10 | **`reRenderMetaAds` campType line** (~line 1562) | add `\|\|geo==='UK'` to the ALL-group branch | UK ads split by creative instead of grouped as one ALL block |
| 11 | **`isAdActive()` geo branches** (~line 4198) | add UK as FIRST branch: `if(/[_ ]UK$/.test(n)) geo='UK';` + matching `geoKey` branch `if(geo==='UK') return /[_ ]UK$/.test(ku);` | UK ad could resolve to wrong geo's status via bareKey fallback |

**Pattern choice:** UK ad names end in `UK` preceded by space or underscore (`_En_ UK`, `_En_UK`, `_GLO_UK`). Use `/[_ ]UK$/i` — anchored to end, won't false-match anything else. Always grep all existing ad names for `[_ ]UK$` to confirm no collisions before committing the pattern.

**Color-index gotcha (item 3):** inserting `uk` BEFORE `cat` in `GK.meta` shifts indices — `cat` moves to index 4. Put the new color at index 3 and keep `cat`'s light-grey at index 4 (`GC=["#1a1a1a","#6B7280","#9CA3AF","#9333ea","#D1D5DB"]`) so Catalogue's dot doesn't change.

**Verify before delivery (simulate each path in Python, don't eyeball):**
```python
# 1) GK.meta contains the new key; GL has label; GC has >= len(GK.meta) colors
# 2) Simulate MTD/Last7/Last30 gr-build: for g in GK['meta']: sum spend over window — new geo shows spend>0
# 3) Simulate detectGeo2 + detectGeo on each new-geo ad name → returns the new label
# 4) Confirm each new-geo ad is 'active' in META_AD_STATUS (exact-key match)
# 5) Confirm no OTHER ad name matches the new geo's regex (no collisions)
```

**Scope:** apply only to the platforms the geo actually runs on. UK is **Meta-only** — do NOT add `uk` to `GK.tiktok/snap/google` or their geo arrays; those tabs have no UK bucket and an empty row would render as `—`.

**The "multiple render paths" mental model:** "the same geo list" appears in at least four conceptually separate components — (a) `GK`/`GL`/`GC` drive the **Market Breakdown** dot-tables; (b) `META_CAMPS` drives the **drill-down** campaign/adset tables; (c) `GEO_GROUPS` / `GEO_GROUPS2` drive the **Ad-level** views; (d) `BUDGET_TREND_CONFIG` drives the **chart**. They do NOT share a source. A new geo touches all four families. Trace the specific component the user is pointing at (read its function, find where its geo list comes from) rather than assuming a previous edit covered it.

---

### RULE 14 — META AD-LEVEL ADS NEED A GEO TOKEN IN THE GRANULAR KEY (bare `_En_GLO` names get dropped)

The Meta Ad-level views bucket ads into geos purely by parsing the GRANULAR ad **key** through `detectGeo` / `GEO_GROUPS` (static table) and `GEO_GROUPS2` (period-button view). **No geo token in the key → `detectGeo` returns null → `if(!geo) return;` silently drops the ad from EVERY geo bucket — it appears nowhere.** Most ad names carry a suffix (`_Meta_UAE_Sales_ASC`, `_Meta_Ku&Qat_Sales_ASC`, `_Meta_KSA_Sales_ASC`, `[_ ]UK$`), but new creatives sometimes land under a bare clean name (e.g. `541_Minime0526_..._En_GLO`) where only ONE geo's instance kept the bare name and the other geos' instances got distinct suffixed names. KU pattern: `/_Ku[\s_&]|Ku\s*&\s*Q/i`.

**Symptom:** "KU/QA/BH active ads shows only 1 (should be N)". The one that shows is whichever carries the geo token; the bare-named siblings are dropped.

**Fix — re-key the GRANULAR Meta ad entry to carry the geo suffix** (matches the file's own convention; do NOT add a name→geo override map in the renderer):
1. Confirm each bare ad's true ad set: per-ad pull `fields=date,ad_name,adset_name,cost,purchases,purchase_value,action_omni_add_to_cart ; filter: ad_name =@ <stem> AND adset_name =@ KUW-QAT-BH_ALL`.
2. Rename the bare key `"<n>_..._En_GLO"` → `"<n>_..._En_GLO_Meta_Ku&Qat_Sales_ASC"`.
3. **Scope the str_replace to the Meta `ads` byte-range** (before the TikTok ad keys, ~pos 626k) — the SAME bare key string can exist in other platforms' GRANULAR objects further down the file. Replace the full unique `"key":[array]` substring and `assert count==1`.

**SHARED-NAME TRAP (critical):** a bare `_En_GLO` name can belong to MULTIPLE Meta ad sets at once — typically a Sales ad set AND the Followers ad set (same creative name). Ingest aggregates by ad name, so the bare GRANULAR entry is the SUM across all ad sets it appears in (sales + followers), which over-counts the geo row. Jun 4 example: `543_..._En_GLO` stored $9.31 = KU-sales $5.31 + Followers (KSA $2.56 + KU $1.44). Must **split**: pull the ad's per-day series scoped to the Sales ad set only (`adset_name =@ KUW-QAT-BH_ALL`), replace the bare entry's array with that Sales-only series, and leave the Followers slice in the Followers bucket (the SALES per-ad entry must exclude Followers spend; the Followers per-ad slice is maintained separately in `META_FOLLOWER_ADS` for the BY COUNTRY — AD SET sub-rows). Clean ads with no Followers instance (Jun 4: 541, 545) → rename only, value unchanged.

**Verify before delivery:** active KU ads' TARGET-day sum (spend/conv/sv/atc) == `D.meta.ku` to the cent, and `detectGeo` routes every one to `KU / QA / BH`.

**Next-ingest rule:** when ingesting Meta per-ad, if an ad's `adset_name` is a geo Sales ad set (`KUW-QAT-BH_ALL`, `UAE ALL`, etc.) but the ad name has no geo token, append the geo suffix to the GRANULAR key at ingest — and if that bare name also carries Followers spend, keep only the Sales-ad-set slice in the per-ad entry.

---

### RULE 15 — GOOGLE CAMPAIGNS RENDER GROUPED BY COUNTRY (not raw spend / not key order)

Google campaign names are `TYPE_COUNTRY_..._goog` (`PMAX_KSA_Pyjama_EN_goog`, `SEM_UAE_Brand_EN_goog`, …). Default render had them sorted by spend-desc (CAMPAIGNS card) or raw object-key order (overview table), so the same country's rows scattered down the list and the eye had to jump around. They now cluster by country, PMAX before SEM within each country, then spend-desc.

**Shared comparator (defined once, just above `buildGoogleCampsHTML`):**
```js
function _googCountryKey(name){
  const n=(name||'').toUpperCase();
  if(/UAE[_\-]?KSA/.test(n)) return 4;            // multi-geo PMAX -> last
  if(/KSA/.test(n)) return 0;
  if(/UAE/.test(n)) return 1;
  if(/KUW|QAT|\bKW\b|\bQA\b|\bBH\b/.test(n)) return 2;
  return 3;
}
function _googSpendOf(x){ return (x&&x.agg&&typeof x.agg.spend==='number') ? x.agg.spend : (x.spend||0); }
function _googCampCmp(a,b){
  const ca=_googCountryKey(a.name), cb=_googCountryKey(b.name);
  if(ca!==cb) return ca-cb;                       // group by country
  const ta=/^PMAX/i.test(a.name)?0:1, tb=/^PMAX/i.test(b.name)?0:1;
  if(ta!==tb) return ta-tb;                        // PMAX before SEM
  return _googSpendOf(b)-_googSpendOf(a);          // then spend desc
}
```
Country order: **KSA(0) → UAE(1) → KUW-QAT(2) → other(3) → multi-geo all-geo PMAX(4, last).** The multi-geo `PMAX_UAE_KSA_KW_QA_Abaya_EN_goog` is checked FIRST (`UAE_KSA` test) so it lands in the all-geo bucket instead of falling into KSA/UAE.

**THREE render sites — all must use `_googCampCmp` (rows shape differs, hence `_googSpendOf`):**
| Site | Function (~line) | Row shape | Was |
|---|---|---|---|
| CAMPAIGNS card — all-time/MTD | `buildGoogleCampsHTML` (~768) | `{name, spend, …}` | `rows.sort((a,b)=>b.spend-a.spend)` |
| CAMPAIGNS card — Last 7/Last 3 day-breakdown | `buildGoogleCampsHTML` (~741) | `{name, spend, …}` | `rows.sort((a,b)=>b.spend-a.spend)` |
| OVERALL PERFORMANCE BY CAMPAIGN overview (green-dot GOOGLE block) | `gCamps` build (~1741) | `{name, agg:{spend,…}}` | unsorted (raw `Object.entries` key order) |

`_googSpendOf` reads `.agg.spend` when present (overview rows) else `.spend` (card rows), so one comparator serves both shapes. The Adset Overview table groups Google by **geo** (3 rows: UAE/KSA/KU), not by campaign — leave it alone.

**Verify after editing:** `grep "rows.sort(_googCampCmp)"` returns 2 (card) + `gCamps … .sort(_googCampCmp)` once; extract `<script>` bodies and `node --check`; single defs of each helper.

**To change country order** (e.g. UAE-first), reorder the integer returns in `_googCountryKey` — nothing else changes.

### RULE 16 — SNAP ACTIVE ADS RENDER PER-GEO (a creative runs in MULTIPLE geo squads at once)

**The trap:** the Active Ads card on the Snap tab groups by geo (UAE / KSA / KU-QA-BH). But a single Snap creative is almost always **live in several geo squads simultaneously** (e.g. Jun 9–15: `548` ran UAE+KSA+KU, `527`/`536` ran UAE+KU). The old model mapped each clean ad name to ONE geo via `SNAP_AD_GEO`, so it dumped the ad's WHOLE spend into one section and never showed it in the other geos it ran in. Symptom: a geo section (usually **KU/QA/BH**) looks light / "missing active ads," while another geo over-reports that ad's spend. `D.snap.<geo>.spend` won't reconcile to the ads shown.

**Root data fact:** `GRANULAR.snap.ads[name]` holds one daily series per ad = the ad's total across all its squads. Geo attribution at the ad level is NOT in that series — it must come from a per-`ad_squad_name` pull. The Snap Active Ads card is ALWAYS last-7 (or last-3) — so only a 7-day per-geo split is needed.

**Fix architecture — `SNAP_GEO_SPLIT_DAILY` (regenerate EVERY Snap ingest, like `SNAP_AD_GEO`):**
A top-level const consumed inside `buildSnapAdsHTML` (defined just after `SNAP_AD_STATUS`). Shape:
```js
const SNAP_GEO_SPLIT_DAILY = {
  "UAE":          { "<makeSnapDn(name)>": { "Jun 9":{spend,sv,conv,atc}, … } },
  "KSA":          { … },
  "KU / QA / BH": { … }
};   // geo labels MUST be exactly "UAE","KSA","KU / QA / BH" (match SNAP_GEO labels)
```
`buildSnapAdsHTML` has a `if (typeof SNAP_GEO_SPLIT_DAILY !== 'undefined')` branch that builds `merged[geoLabel][dn]` + `SNAP_AD_DAILY_CACHE` directly from it (bypassing `detectSnapGeo`/`isSnapAdActive`/ratio-scaling for the active card). Leave the legacy `else` branch in place as fallback.

> ⚠️ **Because that branch bypasses `isSnapAdActive`, the panel showed PAUSED-but-recently-spent ads as running.** Fixed Jun 2026 by adding `const SNAP_GEO_ACTIVE = {"UAE":[nums],"KSA":[nums],"KU / QA / BH":[nums]}` (right after `SNAP_AD_STATUS`) and a filter at the top of the split branch that skips any ad whose leading number isn't in `SNAP_GEO_ACTIVE[geoLabel]`. **`SNAP_GEO_ACTIVE` MUST be rebuilt EVERY Snap ingest** from the squad-level `ad_status` window pull (a number is active in a geo iff `ad_status==ACTIVE` in ≥1 squad of that geo; an ad ACTIVE in KSA but PAUSED in UAE goes in KSA only). This is now the thing that makes the Snap ADS panel match Ads Manager's running ads — it is geo-specific, unlike the base-name `SNAP_AD_STATUS`. If you forget to refresh it, the panel silently keeps showing last cycle's active set (classic silent decay). `verify_ook.py` checks it exists and its nums are in the split, but canNOT verify freshness offline. Confirmed regression: 547(UAE), 548(KSA), 527/536(KU) were shown as running while PAUSED in those geos.

**How to build it each ingest (pull → split → reconcile):**
1. Pull per-(ad × squad × day), ACTIVE rows only:
   ```
   ds_id=SCM  account=b845ada9-4b9d-481a-9032-08012a6b89b4
   fields=date,ad_name,ad_squad_name,ad_status,cost,conversion_purchases,conversion_purchases_value,conversion_add_cart_swipe_up
   settings={"action_report_time":"impression","attribution_window":"1_DAY__7_DAY"}
   date range = last 7 days of the file (the latest ingested day back 6)
   ```
2. Squad → geo label: `UAE…`→`UAE`, `KSA…`→`KSA`, `KW/QA/BH…`→`KU / QA / BH`. Drop `ad_status==PAUSED` rows entirely (paused ads must NOT render even with residual spend).
3. **Keep each ad's existing FILE daily totals** (`GRANULAR.snap.ads[name]` for those 7 days) and SPLIT them across the geos that ad ran in, per day, by the API per-geo **spend share** — same largest-remainder method as RULE 14/GCC-PMAX:
   - `spend` = API geo cost rescaled so the day's geo-spends sum to the file's daily spend (fix the rounding cent on the largest-share geo).
   - `sv` = file daily SV × geo spend-fraction (fix rounding cent on largest share).
   - `conv`, `atc` = **largest-remainder integer** allocation of the file daily integer across geos (sum is preserved exactly).
   - Single-geo ads → 100% to their one geo (totals unchanged).
   - `makeSnapDn(name)` produces the display key — replicate the HTML regex exactly so labels match (clean GLO names → no geo suffix; names containing `_Snapchat_KSA_…` → ` [KSA]`).
4. Do NOT re-derive conv/SV totals from this fresh pull — the default-attribution pull commonly reports higher conv/SV than the file (maturation drift; that is RULE 11's job via a `redo`, not this card). This rule only re-distributes the file's accepted per-ad totals across geos.

**Blocking reconciliation asserts (pre-delivery):**
- Per ad: Σ(split spend over geos) == file period spend (±$0.05); Σ conv == file conv (exact); Σ atc == file atc (exact).
- Per geo: Σ(split weekly spend) == `D.snap.<geo>` weekly spend **minus paused-ad spend** in that geo (the only allowed delta is paused creatives, e.g. `506` KU, `546` KSA, `541`/`542` UAE).
- Render sim: each geo section lists exactly the ACTIVE ads that ran in that squad — KU/QA/BH must include every multi-geo creative that touched a `KW/QA/BH` squad, not just KU-exclusive ones.

**`SNAP_AD_GEO` companion map:** values MUST be UPPERCASE (`"UAE"`/`"KSA"`/`"KU"`). The `detectSnapGeo` fallback is now case-insensitive (`String(SNAP_AD_GEO[n]).toUpperCase()`) so a lowercase value can no longer silently drop an ad — but still write entries uppercase. This map only matters for the legacy fallback path now; the active card reads `SNAP_GEO_SPLIT_DAILY`.

---

### RULE 17 — JAVASCRIPT DUPLICATE OBJECT KEY TRAP (silent data override)

**The trap:** JavaScript silently ignores duplicate keys in an object literal — the LAST occurrence wins. If `GRANULAR.tiktok` contains `ads:{...correct Jun data...}` followed by a second `ads:{...stale Apr/May data...}` (both inside the same `tiktok:{}` wrapper), the browser reads ONLY the stale second block. No error is thrown. `node --check` passes. The file looks correct. The dashboard shows wrong data.

**How it happens:** During a GRANULAR patch, new `ads:{...}` block is appended after the first one instead of replacing it. The Python string search (`content.find('ads:')`) finds the FIRST occurrence (correct) and "patches" it — but the second stale block remains further down and wins in the browser.

**Confirmed case (Jun 18 2026):** TikTok ADS panel showing Jun 16 (not Jun 17) after a full Jun 17 injection. Python inspection showed all 15 ad keys with Jun 17 data. But Node.js `eval()` of the actual GRANULAR.tiktok string showed 84 keys from Apr/May only — because a second `ads:{}` block (80KB, stale) sat immediately after the correct first block inside `tiktok:{}`. Deleting the stale second block fixed it instantly.

**Detection:**
```python
# After ANY GRANULAR injection, scan the platform section for duplicate keys:
tiktok_start = content.find('tiktok:{')
snap_start   = content.find('snap:')
tiktok_block = content[tiktok_start:snap_start]

# Count occurrences of each top-level key:
import re
for key in ['adsets:{', 'ads:{']:
    count = tiktok_block.count(key)
    assert count <= 1, f"DUPLICATE KEY: '{key}' appears {count} times in tiktok block — delete the stale one"
```

**Fix:** Find both blocks by byte offset. Delete from the END of the correct block to the end of the stale block (inclusive). Never blindly replace the first match.

**Prevention rule:** When injecting a new `ads:{}` or `adsets:{}` block into a GRANULAR platform section, ALWAYS:
1. Find the existing block start and end by brace-counting (not string replace)
2. Replace the ENTIRE existing block content (start-to-end) with the new content
3. After replacement, re-scan the platform section for duplicate keys before saving

**Why Python hides this:** `content.find('ads:{')` returns the FIRST occurrence and everything looks correct. Only the browser's JS engine (or `eval()`) reveals the duplicate-key resolution. When debugging "data looks fine in Python but wrong in browser" — the FIRST thing to check is duplicate keys in the GRANULAR object.

---

### RULE 38 — TIKTOK "ACTIVE ADS" = THE MANAGEMENT ROSTER, SHOWN EVEN AT ZERO SPEND. STOP GUESSING FROM DELIVERY. [Aug 6 2026]
> ⚠️ **SUPERSEDED as the primary method (Aug 20 2026):** the authoritative source is now the Ads Manager **Status** field (ON=Active / OFF=Paused), resolved per `(ad, geo)` — see "★★ TikTok ACTIVE/INACTIVE — READ THE STATUS FIELD" in the CURRENT CAMPAIGN STATE block near the top. The management roster below still lags live toggles, so the user's Status screenshot always overrides it and manual per-geo curation is preserved across ingests. The zero-spend/roster logic in this rule remains only as a fallback.

**The user has said this many times. This is the definitive, permanent rule — do not re-derive it, do not guess from spend, do not ask again.**

An ad's TikTok active/inactive state comes from its **status**, read from the management roster (`campaign_and_resource_get`, `campaign_detail_level: ad`) for the ads inside the active campaign (`GCC | Sales | Prospecting`, id `1870266496222258`). **As of Aug 10 2026 the active adgroups are the three `… | Prospecting | July 2026` adgroups (560-564); the three `… | Sale 40% | July 2026` adgroups are status PAUSED — so every ad in them is inactive even though the ads themselves still read ENABLED (adgroup status overrides ad status).** See the CURRENT CAMPAIGN STATE block near the top for the live adgroup IDs and active ad list.

1. **An ad ENABLED in the roster is ACTIVE — render it even with $0 spend / 0 impressions.** New ads (e.g. `559_Abaya0126_Wm_Vid short_Vert_UGC VO_En` launched in the Ku adgroup) will have no reporting rows at all, because the TikTok reporting API only returns ads that delivered. So the **roster is the source of truth for which ads exist and are on** — not the reporting pull. To make a zero-spend active ad render, add a `GRANULAR.tiktok.ads` key `"<ad_name>_Tiktok_<UAE|KSA|Ku/Qa/BH>_Sale"` with a single latest-day record of all zeros, and set `TIKTOK_AD_STATUS[thatKey]='active'`. The panel (`buildTTAdsHTML`) requires both `isTTAdActive` true AND ≥1 record in the shown period, so the zero record is what makes it appear (as Active with dashes).

2. **The only exception — a paused ad whose status field is lagging.** All three API status fields (`ad_opt_status`, `ad_status`, and the roster `status`) can still report `ENABLE` / `AD_STATUS_DELIVERY_OK` for ~a day after the user pauses an ad (confirmed on `556 FINAL HOURS` in KSA and Ku: roster/opt_status said ENABLE while the ad sat at $0/0 impressions and the user had turned it off). So: **an ad that previously delivered and has now dropped to 0 impressions on the latest day while its geo-mates are spending is OFF** — mark it `inactive` regardless of what the status field says. Distinguish from case 1 by history: never-delivered + ENABLED = new/active (show at zero); previously-delivered + now 0 = paused (hide). When the user says an ad is off, trust them immediately.

3. Do **not** use `AD_STATUS_DELIVERY_OK` from the reporting `ad_status` field as the activity signal (it's the stale secondary status and omits zero-delivery ads). Ignore rows in disabled campaigns (`ad_status = AD_STATUS_CAMPAIGN_DISABLE`, e.g. old `559_PlusSizes` Interest-adgroup rows) — those are a different creative in a dead campaign.

Net: rebuild `TIKTOK_AD_STATUS` every session from the roster; flip to inactive the paused-but-lagging ones caught by the 0-delivery test or a user report. Snap uses `SNAP_GEO_ACTIVE` (number list, RULE 35); Meta uses exact `META_AD_STATUS` (RULE 37); TikTok uses this.

**CRITICAL — do NOT seed every ENABLED roster ad. Only seed a zero record for a GENUINELY-NEW ad (one that has NEVER delivered in that geo — no prior `tiktok.ads` records at all).** A `559`-type ad just launched in the Ku adgroup with no history → seed zero + active (correct). But an ad that **previously delivered and then dropped to $0** (e.g. `227`/`397`/`543` in Ku, `487` in UAE, `543` in KSA — all had July delivery then went to 0 in August) is the **paused-lagging** case: the roster still says ENABLED but the ad is OFF, and it must be `inactive` / hidden, NOT seeded. Test per `(num, geo)`: latest existing `tiktok.ads` record is old + zero recent delivery → **paused, hide**; no record ever + ENABLED in roster → **new, seed+active**; recent delivery → active, real data. Over-seeding stopped ads makes the panel show dead ads with empty 7d/3d breakdowns — the user flagged exactly this. When unsure, hide it and ask.

---

### RULE 37 — META "ACTIVE ADS" = EXACT `META_AD_STATUS` ENTRY PER meta.ads KEY; NEVER RELY ON THE NUMBER-COLLISION FALLBACK [Aug 3 2026]

The Meta ADS panel shows an ad in a geo iff **(a)** it has a `GRANULAR.meta.ads` key, **(b)** `isAdActive(baseName)` is true, **(c)** `detectGeo2` resolves. `isAdActive` tries an **exact** `META_AD_STATUS[baseName]` first, then falls back to a **number-prefix match** (any status key with the same leading number + geo), then defaults to inactive. **The number-prefix fallback is a bug source** — creatives that share a number but differ (`AI | 177` vs `177_Allure`; `487_FINAL HOURS` vs regular `487`; `559_Abaya` vs `559_PlusSizes`; regular `556` vs `556 FINAL HOURS`) inherit each other's status, so a paused ad renders active (and vice-versa).

**Two symptoms seen (Aug 3):** `562` and `177` rendered in KSA though paused (fallback matched an active same-number key); `559_Abaya` was missing from UAE (no meta.ads key at all).

**The rule — every ingest, after pulling live Meta ad status (`campaignobjective != OUTCOME_TRAFFIC`, filter to the last few days so recently-run ads are included):**
1. **Add any active+delivering sales creative that has no meta.ads key** (e.g. `559_Abaya`, `527`) as `"<ad_name>_Meta_<GEO>_Sales_ASC"` with the day's row — otherwise it can never render.
2. **Write an EXACT `META_AD_STATUS` entry for every meta.ads sales/catalogue key**, keyed by the panel's `baseName` (the meta.ads key with date/`_v`/` - Copy` suffixes stripped), set from the live pull by matching **(ad_name normalised of ` - Copy N`, adset-geo)** → ACTIVE/PAUSED. Anything not present in the live window → `inactive`. This makes `isAdActive` always hit the exact branch and never the number fallback.
3. Geo tokens: `_Meta_UAE_`, `_Meta_KSA_`, `_Meta_Ku&Qat_` ; adset `KSA_ALL`→KSA, `KUW-QAT-BH`→Ku, `UAE_ALL`→UAE, `catalogue`→CAT. Distinguish variants by **full creative name + geo**, not number alone.
4. **Status flips fast** — Meta toggles changed within hours of the Aug-3 data pull (`562` was ACTIVE at data-time, PAUSED at check-time). When the user reports a live/off mismatch, re-pull status fresh and trust the live toggle over the data-day status.

**Snapchat** uses `SNAP_GEO_ACTIVE[geo].includes(num)` — an explicit per-geo number list (no collision); keep it rebuilt from the 3-level live status every ingest (RULE 35). **TikTok** panel uses exact `TIKTOK_AD_STATUS[baseName]==='active'` — clean as long as every ENABLED roster creative has an active entry. Both were correct; the collision problem is **Meta-specific**.

---

### RULE 36 — `GRANULAR.snap.ads` (SNAP TOP-ADS PANEL) MUST BE REFRESHED EVERY INGEST — IT IS A SEPARATE STORE FROM `SNAP_GEO_SPLIT_DAILY` [Aug 3 2026]

> **The Snap per-ad breakdown has TWO independent stores. Update BOTH every session:**
> 1. `SNAP_GEO_SPLIT_DAILY` — drives the Snap **Active Ads / geo-split** panel (RULE 18). ← was being maintained.
> 2. `GRANULAR.snap.ads` — drives the Snap **Top Ads** panel, exactly parallel to `GRANULAR.meta.ads` and `GRANULAR.tiktok.ads`. ← **was silently missed for 3 sessions (stuck at Jul 30 while D.snap/adsets were current).**

**Failure mode caught (Aug 3):** the pipeline updated Snap platform + adset totals (`D.snap`) and `SNAP_GEO_SPLIT_DAILY` to the latest day, but never touched `GRANULAR.snap.ads`, so the Snap Top-Ads panel froze at Jul 30 even though everything else read current. `verify_ook.py` did not catch it (snap.ads is not gated). **Fix:** treat snap.ads as a first-class per-ad store — whenever meta.ads / tiktok.ads get the new day, snap.ads gets it too.

**Mechanics:**
- Keys: `"<full ad_name>_Snap_<GEO>_Sale"` with `GEO ∈ {KSA, UAE, Ku}` for the July-Sale ads (retargeting variants use `_<GEO>_Ret` and are historical — leave them). Schema `{d,spend,sv,conv,atc,roas,cpo,avgpv}`, **sv is USD-native** (Snap), `avgpv = sv/conv if conv>0 else 0.0`.
- Match each delivering `(num, geo)` from the validated Snap raw to its existing Sale key; **prepend** the new day(s), newest-first, dropping any pre-existing entry for those dates first.
- **A creative that newly enters the Sale squad may have no Sale key yet** (only an old `_Ret` key) — e.g. Aug 3: `527` (KSA) and `559` (KU). **Create** the Sale key from the current ad_name; the render-collision rule (filter entries with no spend in last 7 days) resolves the number collision against the stale `_Ret` key.
- Per-key `latest` legitimately differs by ad (a geo the ad stopped delivering in stays at its last active day — e.g. `397/KSA` stops Jul 31, `487/KU` at Jul 27). Only the **global** latest across snap.ads must reach LATEST.
- Sanity: Σ spend over all `_Snap_*_Sale` keys for a day == `D.snap` spend (± penny), conv exact.

---

### RULE 35 — SNAPCHAT ON = DELIVERY STATUS "Delivering", OFF = "Not Delivering" [Jul 31 2026]

> **DEFAULT REFLEX (Jul 31):** to decide if a Snap ad is ON or OFF, read the **Delivery status** column. **"Delivering" = ON. "Not Delivering" = OFF.** It's that simple — the Meta/TikTok analog (RULE 32 / RULE 33), for the third platform.

**Supermetrics mapping (there is NO literal "Delivering" field, and Snap has NO management API):** the config-status fields are `ad_status`, `ad_squad_status`, `campaign_status`, each returning **`ACTIVE` / `PAUSED`**. "Delivering" is the *effective* state across all three levels:

> **ON (Delivering) ⟺ `ad_status == ACTIVE` AND `ad_squad_status == ACTIVE` AND `campaign_status == ACTIVE`.** If ANY level is `PAUSED` → **Not Delivering (OFF)**.

Reading `ad_status` alone is not enough: an ad can be `ACTIVE` while its squad or campaign is paused → it is **Not Delivering** and must be `inactive` in `SNAP_AD_STATUS`. (Same trap as the TikTok 556/KSA case in RULE 34: ad ENABLE but campaign disabled = not delivering.) **Method:** pull `fields=ad_name,ad_status,ad_squad_status,campaign_status` for the latest day (no status filter), set `active = (all three == ACTIVE)`, everything else `inactive`. Keep the geo-suffixed key convention. Since Snap has no management API, these three status fields ARE the source of truth — plus RULE 31 (the client's screenshot outranks the API if a very-recent toggle hasn't propagated).

---

### RULE 34 — TIKTOK: AN "ACTIVE" AD WITH $0 WINDOW SPEND IS INVISIBLE TO THE REPORTING PIPELINE — SEED IT; AND THE ADS PANEL MUST BE MULTI-GEO (markets SET, not single market) [Jul 31 2026]

**Symptom (Jul 31):** client said "TikTok KSA — 556 missing, should be ON." 556 (FINAL HOURS creative) was genuinely ENABLED in the `KSA | July 2026` ad group (management API + `ad_opt_status == ENABLE` per RULE 33) but had **$0 spend / 0 impressions** in the window (freshly added, not yet delivering).

**Two independent bugs caused the miss — both must be fixed:**

1. **Reporting-invisibility (data side).** The ads panel + `TIKTOK_AD_STATUS` are built from the reporting-data pull, which only returns ads that *delivered* (spend/impr > 0). An ad the Status column marks Active but that hasn't spent yet has **no GRANULAR key** → nothing to mark active → can't render. This is the render-side inverse of RULE 27 (which correctly keeps not-yet-spending *adsets* off). **Fix:** after building the reporting-driven GRANULAR each session, pull the management-API ENABLED roster (`campaign_and_resource_get`, `campaign_detail_level: ad`) and diff `(num, geo)` against the GRANULAR key set; for any ENABLED ad missing from GRANULAR, **seed a zero record** (`{"d":"<latest>","spend":0,"sv":0.0,"conv":0,"atc":0,"roas":0.0,"cpo":0.0,"avgpv":0.0}`) under the correct geo-suffixed key and mark it `active`. Watch the key variant: the KSA 556 uses the `556_FINAL HOURS Abaya0126 SS...` creative → key `..._Tiktok_KSA_Sale`, paralleling the existing KU FINAL HOURS key — NOT the legacy `556_Abaya0126_Wm_...` (that one lives in a disabled `KSA - May 26 - Interest` campaign and reads `AD_STATUS_CAMPAIGN_DISABLE`, $0 — a decoy).

2. **Single-market collapse (render side).** `buildPlatAdsRows` merged ads by a 50-char `baseName` and assigned **one** `market` (last-variant-wins), so same-creative cross-geo Sale ads (397/487/489/499/227, all with `_Tiktok_KSA_Sale` + `_Tiktok_Ku..._Sale` variants sharing a baseName) collapsed to their UAE/KU sibling and the **KSA tab rendered 0 TikTok rows**. The Meta path (`renderTopAdsInner`) already solved this with a `markets` **Set** + `markets.has(marketFilter)`. **Fix (applied):** give `platMerged[baseName]` a `markets:new Set()`, `.add(mkt)` for every variant, keep `market` as the first non-`other` primary, and filter with `if(marketFilter!=='all' && !(markets&&markets.has(marketFilter))) return null;`. Keeps the `agg.spend<=0 return null` guard (RULE 30 hide-when-empty preserved) — a creative with spend in *any* geo now shows under *each* of its geo tabs; a fully-dark creative still hides. Result: KSA went 0→5 rows (397/489/487/227/556), 556 shows in **both** KSA and KU, UAE unchanged.

**Takeaway:** "is it ON" (RULE 33, `ad_opt_status`) and "does it render" are separate questions. An ON ad can be missing for either reason — a $0 reporting gap (seed it) or a render-merge that drops its geo (markets Set). Check both.

---

### RULE 33 — TIKTOK ON = STATUS "Active" (`ad_opt_status == ENABLE`), OFF = "Paused" (`DISABLE`) [Jul 27 2026]

> **DEFAULT REFLEX (reaffirmed Jul 31):** to decide if a TikTok ad is Active or Paused, just read the **STATUS field** = `ad_opt_status` (`ENABLE`=Active, `DISABLE`=Paused). It's that simple. Do NOT reason from spend, delivery, or render mechanics to determine on/off — those answer *different* questions (see RULE 34). The Status field is the answer.

**Standing user instruction (Jul 27):** for TikTok, on/off is easy — read the **Status column** (the Active/Paused one), NOT the Delivery/reporting status. In Supermetrics that column is **`ad_opt_status`**: `ENABLE` = **Active** (ON), `DISABLE` = **Paused** (OFF). This is the operation status the client toggles.

**Don't confuse the two TikTok status fields:**
- `ad_opt_status` → operation status → **ENABLE / DISABLE** → maps 1:1 to the Ads-Manager **Status** column (Active/Paused). ← **USE THIS for on/off.**
- `ad_status` → delivery/reporting status → `AD_STATUS_DELIVERY_OK` etc. → this is "is it delivering", not "is it toggled on". Do NOT use it for the active-ads panel.

**Method (mirrors RULE 32):** pull `fields=ad_name,ad_opt_status,cost_usd` over `last_7_days` (NOT single-day, NOT cost-filtered — same trap as RULE 12), then `active = (ad_opt_status == "ENABLE")`, everything else inactive. Keys stay geo-suffixed (`<base>_Tiktok_<UAE|KSA|Ku/Qa/BH>_Sale`).

**Reconciliation with RULE 24a / RULE 31:** RULE 24a preferred the management API and RULE 31 Case B caught `ad_opt_status` lagging a same-day pause (Jul 17: 543/KU read ENABLE hours after the client paused it). So `ad_opt_status` is the primary signal now (it's the Status column the user reads), but it can still lag a *very recent* pause — if the user reports a mismatch, fall back to RULE 31's dark-vs-siblings delivery check ($0 / 0 impressions today while ad-group siblings spend = paused) and sweep the WHOLE latest-day roster (RULE 32), not just one ad. The screenshot always wins.

### RULE 32 — META ON = DELIVERY "Active" OR "Learning" (read the Delivery column, not just ACTIVE) [Jul 27 2026]

> **DEFAULT REFLEX (reaffirmed Jul 31):** to decide if a Meta ad is ON or OFF, just read the **Delivery column**. **Active = ON. Learning = ON** (still delivering — never drop it). **Off/Paused = OFF.** It's that simple — don't reason from spend or anything else to decide on/off. (TikTok analog = RULE 33's `ad_opt_status`.)

**Standing user instruction (Jul 27):** for Meta, the **Delivery column is ground truth for on/off**, and an ad is ON if its Delivery value is **"Active" OR "Learning"** (also "Learning limited"). A newly-launched or recently-edited ad sits in the **Learning** phase — it is delivering and must show in the Active-ads panel. Do NOT treat Learning as off.

**Why this bites:** filtering the RULE 12 status pull to `adstatus == ACTIVE` can drop a Learning ad → it falls to `inactive` → it vanishes from the panel even though the client sees it live. Pull the status field with **no status filter** and classify in Python: `on = delivery in {"Active","Learning","Learning limited"}`. Everything else (Paused, Not delivering, Rejected, etc.) → `inactive`.

**Scan the WHOLE roster, every day.** RULE 31's dark-vs-siblings pause check must run against **every ad on the latest day**, not only the one a fix started from. Precedent: Jul 26 the user flagged 487/UAE off; it had gone dark on the exact same two days (Jul 25–26) as 397/KU, which had already been flipped — the miss was checking one ad instead of sweeping all of them. Combined rule: an ad is ON iff Delivery ∈ {Active, Learning} AND it isn't flatlined ($0 / 0 impressions) while its ad-group siblings spend.

**Jul 27 application:** user said "remove 325, it's off, 0 purchases." `adstatus` had 325/KU as ACTIVE (it spent $17.45 at 0 conv), but the Delivery column showed it off → flipped 325 KU (and confirmed KSA/UAE already) inactive. Meta active 23 → 22. Display-only; its spend stays in the KU totals, Δ=0.00.

### RULE 31 — STATUS FLAGS GO STALE; A USER-REPORTED LIVE/OFF MISMATCH IS VERIFIED BY *TODAY'S DELIVERY*, NOT THE STATUS FIELD [Jul 17 2026]

**The user's Ads Manager screenshot outranks every API.** Both platforms produced stale status on the SAME day. Do not push back on a reported mismatch using a status flag as evidence — check delivery first.

**Case A — Meta, `adstatus` is status AS OF PULL TIME (not per-date).** Jul 16 ingest pulled `adstatus == ACTIVE AND cost > 0` and 487/KSA came back ACTIVE (it really did spend $11.31 that day). Hours later the user reported it off; a re-pull returned **PAUSED**. Meta's `adstatus` is the ad's *current* effective status stamped onto every date row — it is NOT the status on the queried date. So a morning ingest's status map can be stale by afternoon if the client pauses mid-day. (Same semantics as Snap — see the Jul 15 note.) The numbers stay right; only the active/inactive flags drift.

**Case B — TikTok, BOTH status sources lied (this AMENDS RULE 24).** Same day: user reported TikTok 543 off in KW/QA/BH. `campaign_and_resource_get` (the "source of truth" per RULE 24) returned **ENABLED** on a fresh, cache-busted call; reporting `ad_opt_status` returned **ENABLE / AD_STATUS_DELIVERY_OK**. Both were WRONG — the user's screenshot showed the toggle off. RULE 24 says the management API is authoritative for TikTok; **that is only true for pauses that are not recent.** TikTok's status endpoints can lag hours behind a pause, and Supermetrics caches on top.

**The reliable check (use this every time):** pull per-ad `cost + impressions` for **TODAY** (the in-progress day), scoped to the ad group / geo in question, and compare siblings:
```
fields=ad_name,adgroup_name,ad_opt_status,ad_status,cost_usd,impressions   # TIK
start_date=end_date=<today>
```
An ad sitting at **$0 spend / 0 impressions today while every sibling in the same ad group is spending** is PAUSED — regardless of what the status flag claims. Jul 17 proof: KW/QA/BH 397=$28.39, 227=$27.22, 487=$20.72, 489=$17.96, **543=$0 / 0 impressions** → 543 paused, exactly as the screenshot showed. Meanwhile 543 KSA ($19.52) and 543 UAE ($18.30) were still delivering → the pause was per-geo, so ONLY flip the (num,geo) that flatlined.

**Procedure when the user says "X should be hidden":**
1. Do NOT argue from the status flag. Pull today's per-ad cost+impressions for that geo/ad group.
2. Flatlined vs spending siblings → mark that exact `(num, geo)` key inactive. Leave the other geos alone.
3. Run the RULE 29 sweep afterwards so the number can't resolve back via the number+geo prefix fallback.
4. Re-pull the FULL roster (cost filter, NO status filter) rather than patching one key — a client pausing one ad is usually pausing several. Jul 17 Meta: only 487/KSA had changed; TikTok: only 543/KU.
5. Display-only. The paused ad's spend stays in the geo/adset totals (it did spend), so reconciliation must remain Δ=0.00.

### RULE 30 — HIDE-WHEN-EMPTY, NEVER DELETE (markets/rows that go dark) [Jul 15 2026]

**The rule, in the user's words: "hiding not deleting stuff, so they would show up when they were ON on certain days we pick."** When a market/row stops running (UK went to $0 on Jul 14; Catalogue_GCC_ADV+ ended Jun 25), do NOT delete its bucket, its `GK` key, its `GL` label, or its history. Deleting hides it today but DESTROYS the back-history — picking Jul 1–9 must still show UK with its real spend. Instead, render conditionally on whether the row has data **in the selected date range**.

**Implementation (in file):** a single shared predicate next to `const GL=`:
```js
const hasRangeData = x => (x.spend||0) > 0 || (x.conv||0) > 0 || (x.sv||0) > 0;
```
applied as `.filter(hasRangeData)` to EVERY `const gr=geos.map(...)` market-row builder. There are **7** of them and they must ALL be patched or views disagree: `renderPlatRange` (~L1634), `buildMTDMarketTable` (~L3332), `buildLast7MarketTable` (~L3397), `buildLast30MarketTable` (~L3456), **`buildMetaMBInner` (~L3514 — this is the one users see: the card with Yesterday/7d/30d/MTD/Custom pills, `buildMetaMBCard`)**, `renderPlat` (~L3666, currently dead code behind `${false?` but patch anyway), `renderPlatMTD` (~L4621). All 7 return a uniform `{spend,sv,conv}` shape, so one predicate covers them all. **Filter AFTER `.map()`, never before** — the color index `i` comes from position in `geos` (`GC[i]`), so filtering first would shift every row's colour.

**Precedent — this pattern already existed, follow it:** the Meta adsets panel used `.filter(a => a.agg.spend > 0 || a.isFollowers)`, and the Followers row in `buildMetaMBInner` self-hides via `fSp>0?…:''`. RULE 30 just makes it universal and range-aware.

**Generalises for free:** any future market that goes dark drops out on recent dates and returns on historical ranges with zero code changes. Verify by simulating the aggregate per range before delivering (Jul 14 → 4 rows, UK hidden; Jul 1–9 → 5 rows, UK $1,761.83 back; Jun 18–25 → 6 rows, UK + ADV+ both back). Display-only: reconciliation is untouched (a $0 row contributes nothing to any sum).

**Corollary — renaming a live campaign:** change the DISPLAY labels only; never rename the data key. Jul 15 2026 the followers campaign was renamed `Followers_GCC Markets_Brand_MF-Prospecting-Standard` → `Followers_ALL Markets_Brand_MF-Prospecting-Standard`, so `name:'Followers - GCC Brand'` (~L1786) → `'Followers - ALL Markets Brand'` and `geo:'Followers – Brand GCC'` (~L1937) → `'Followers – Brand ALL Markets'`. The key `META_FOLLOWERS_KEY = "Followers GCC - Brand"` (~L3806) stays as-is — every day of history in `GRANULAR.meta.adsets` + the budget map is stored under it; renaming would orphan all of it for zero visible gain. Same logic as RULE 30: the display can change, the data spine cannot.

### RULE 29 — PHANTOM-ACTIVE VIA `isAdActive` PREFIX FALLBACK (stale keys render with dashes) [Jul 11 2026]

Extends RULE 25. `isAdActive` falls back to matching by ad NUMBER + geo when a key is not an exact match in `META_AD_STATUS` — so a STALE granular key (old creative, no recent data, absent from the status map) resolves onto the *active* same-number/same-geo sibling and RENDERS as active with an all-dashes row. Jul 11 2026: KU panel showed 7 ads not 5 — two stale keys (`487_…UGCO VO…_Meta_Ku_Sales_ASC`, `489_…Transition…_Meta_Ku_Sales_ASC`, older single-`_Ku_` suffix) prefix-matched onto the active `487SS`/`489SS` Sale keys. Same class hit Catalogue: 5 stale April `_Prospecting` EN_ variants defaulted active via the `isAdActive` EN_ branch (→ 9 catalogue rows instead of 4).

**Fix:** whenever a panel shows MORE ads than the live adset, sweep EVERY geo for keys that (a) are not exact-in-status, (b) resolve active via the number+geo (or EN_) fallback, and (c) have no last-7-day data → mark each explicitly `inactive`. Then re-simulate the render per geo (active + geo-detected, no data filter) and confirm the count matches the live adset. A screenshot from the user is the fastest way to spot this — the extra rows are always the dash rows at the bottom.

### RULE 28 — SALE / NEW-CAMPAIGN CUTOVER: NAMING + WHERE IT LIVES (Jul 2026 Sale_40%)

- **Meta:** the new adset KEEPS the country prefix — `UAE_ALL-…-Sales_40% | JUL2026`, etc. Geo routing by adset name still works; the geo buckets CONTINUE (do NOT create a new bucket). New Sale creatives (544, 397SS, 489SS, 487SS, 543SS) take the usual `_Meta_<geo>_Sales_ASC` / `_En_UK` suffix keys. On the cutover day both old (residual) + new (ramping) spend within a geo — normal.
- **TikTok:** Sale_40% is a SEPARATE campaign, NOT the old prospecting `campaign_id 1831579436999697`. The management pull on the old id shows every adgroup PAUSED, and the new `Uae | July 2026` / `KSA | July 2026` / `KW/QA/BH | July 2026` adgroups live elsewhere → they will NOT appear in a mgmt-by-old-campaign-id pull. Confirm the new ads from REPORTING (cost>0) and key as `<base>_Tiktok_<geo>_Sale`. Names are messy (`one of a kin july 5(2)_….mov_…`, and `Copy 1 of …` for the KSA variant) — strip to the core `<num>_<creative>`.
- **Snap:** new squads are `"<GEO> - Sale 40%- July 2026"` (note the LEADING SPACE on `" KW/QA/BH - Sale 40%…"`). Old retargeting squads wind down to residual pennies. Set `SNAP_GEO_ACTIVE` to the Sale numbers. Sale creatives SHARE ad numbers with old ones (487 exists in both retargeting UGCO and Sale SS) — give the Sale rows a distinct display name (e.g. `… [<GEO> Sale]`) and a distinct granular key (`…_Snap_<geo>_Sale`).
  - **⚠️ A distinct display name is NOT sufficient on its own (Jul 13 2026).** `buildSnapAdsHTML` filters `SNAP_GEO_SPLIT_DAILY[geo]` entries by AD NUMBER: `_num = dn.match(/^(\d+)/)`, then `if (!SNAP_GEO_ACTIVE[geo].includes(_num)) return`. So BOTH the retired `487_…UGCO VO [KSA]` and the active `487_…SS…[KSA Sale]` entries match active number "487" and BOTH render (as long as the retired one still has any spend in the last-7 window from its wind-down) → panel shows 5 ads not 4. The distinct name doesn't help because the match is numeric. **Fix: after a cutover, scan every geo bucket of `SNAP_GEO_SPLIT_DAILY` for a number that appears in >1 entry (a Sale entry + a non-Sale entry); DELETE the retired non-Sale entry.** Only ad numbers reused by the Sale set collide — Jul 2026 that was 487 in KSA only (397/489/543 were never old Snap retargeting ads; 487 only ran KSA). This is display-only (the retired ad's residual spend still lives in the geo/adset totals, so reconciliation is untouched). Verify by re-simulating per geo: entries whose number ∈ `SNAP_GEO_ACTIVE[geo]` AND have last-7 spend should equal the live squad count (4). A user screenshot of the geo panel is the fastest way to catch it.

### RULE 27 — A NEW ADSET CAN SIT AT $0 FOR DAYS BEFORE IT DELIVERS — FLIP STATUS ONLY WHEN ADS ACTUALLY SPEND

When a Sale/new adset is launched, the adset/squad may already appear in pulls (rows present, status ACTIVE) but with $0 spend for several days before it starts delivering. Do NOT flip a platform to the new structure or move status until its new ads have cost>0 in reporting. Jul 2026: Meta's Sale_40% launched AND delivered Jul 9; TikTok & Snap Sale_40% squads were visible as $0 rows from ~Jul 3 but did not DELIVER until Jul 10 — so on Jul 9 only Meta flipped, TikTok/Snap stayed on old ads (which ran the full day). Decide the cutover per-platform from per-ad `cost>0`, never from adset existence alone. Expect exactly one transition day per platform where old (residual) + new (ramping) both spend; that day, record both and flip the old ads to inactive.

### RULE 26 — PAUSED-ADSET RESIDUAL CONVERSIONS: USE THE ADSET-LEVEL GEO BREAKDOWN, NOT THE PER-AD SUM

After a cutover, a paused adset keeps LATE-ATTRIBUTING conversions/SV/ATC at $0 spend for the length of the attribution window (~7 days). The per-ad pull filtered on `cost > 0` MISSES those rows, so the per-ad geo sums fall SHORT of the account total. Jul 10 2026: per-ad summed 61 conv / 15,961 SV / 689 ATC, but account = 66 / 18,051 / 755 — the gap was the paused `…_EN-MAR26` adsets (KSA +1/283.78, UAE +2/610.09, KU +1 atc) still converting at $0 spend.

**Fix:** pull the per-ADSET breakdown with NO cost filter (`fields=ad_set_name,campaignobjective,cost,offsite_conversions_fb_pixel_purchase,offsite_conversion_value_fb_pixel_purchase,offsite_conversions_fb_pixel_add_to_cart`). The paused adsets appear with cost=0 but nonzero conv/sv/atc. Aggregate to geo by the adset-name country prefix INCLUDING those $0 rows, and use THAT for `D.<geo>` and the `meta.adsets` buckets. The per-ad list still drives the `meta.ads` panel (active ads only) — the residual just lives in the geo/adset totals, so the per-ad panel sum legitimately trails the geo total by the residual. The KU country pull (country-level, not cost-filtered) already includes the residual — cross-check KU geo against it; it should match exactly.

### RULE 25 — META STATUS MUST BE RECONCILED TO THE GRANULAR KEY (split-brain variants)

The Meta ADS panel filters each `GRANULAR.meta.ads` key through `isAdActive`, which does an EXACT-match on `META_AD_STATUS` first. When an ad has duplicate UK/geo key variants (e.g. `550_..._En_UK` vs `550_..._En_GLO_UK`), the status resolver (`mres`) and the granular resolver (`mkey`) can pick DIFFERENT variants — so the granular key the panel actually reads ends up marked `inactive` while a phantom sibling is `active`. Result: the ad silently drops from the panel (confirmed Jun 2026: UK showed 3 active instead of 4; `550_..._En_GLO_UK` was inactive while `550_..._En_UK` — which has no granular data — was active).

**Fix every ingest:** after building `META_AD_STATUS`, run a reconciliation pass — for each active `(num,geo)`, resolve the GRANULAR key via the same `mkey` logic and force THAT key to `active`; retire phantom same-num/geo status keys that have no granular data (keeps the active count honest). `verify_ook.py` now has a "split-brain key check" that FAILS if any granular key with latest-day spend is `inactive` while a same-number same-geo sibling status key is `active`. NOTE: Meta "Learning" delivery state = effective status ACTIVE, so Learning ads ARE captured by the reporting status pull — the bug was never about Learning, only about which key variant got the active flag.

### RULE 24a — TIKTOK STATUS MUST COME FROM THE MANAGEMENT API, NOT REPORTING (it is stale) — ⚠️ SEE RULE 31, THIS IS NOT ABSOLUTE

> ⚠️ **AMENDED Jul 17 2026 — the management API is NOT infallible.** On Jul 17 the user reported TikTok 543 paused in KW/QA/BH; `campaign_and_resource_get` returned **ENABLED** on a fresh cache-busted call, and reporting `ad_opt_status` returned **ENABLE / AD_STATUS_DELIVERY_OK**. Both lied — the toggle was off. TikTok's status endpoints lag hours behind a RECENT pause. This rule holds for pauses that have settled; for anything the user reports *now*, verify with **today's delivery** (`cost` + `impressions` = 0 while siblings in the ad group spend) per **RULE 31**. Never argue against a user's screenshot using either status source.

(Numbering note: this was one of two rules numbered 24 — the other is "META MARKET-BREAKDOWN ATC USES TRUE PER-GEO VALUES", now RULE 24b. Renamed to 24a/24b to disambiguate; no content change beyond the amendment above.)

TikTok's REPORTING status (`ad_status` / even `ad_opt_status` in a `data_query`) reflects the ad's status **as of its last delivery in the window**, NOT its live toggle. An ad that delivered earlier in the 7-day window and was then PAUSED still comes back as `AD_STATUS_DELIVERY_OK` / `ENABLE`. Confirmed Jun 2026: dashboard showed TikTok KU = 397,521,542,548,551,552 (6) but Ads Manager toggles showed only 397,548,551,552 ON — 521 and 542 were paused-in-KU (542 still ON in UAE/KSA). 

**Fix / required source:** pull live status from `campaign_and_resource_get` (ds_id=TIK): list campaigns → find the ENABLED campaign(s) → fetch with `params={campaign_detail_level:'ad', campaign_id:...}` → an ad is active in a geo iff campaign.status==ENABLED AND ad_group.status==ENABLED AND ad.status==ENABLED, keyed by ad_group (geo). Rebuild `TIKTOK_AD_STATUS` so ONLY those (num,geo) are active. Watch ad-name `_` splitting and that the same number can be ON in one geo and PAUSED in another.

**Meta & Snap are NOT affected** — their reporting effective/configured status IS live (they correctly return PAUSED for ads that spent in the window, e.g. Meta 505/550-UAE/547, Snap 547). Keep using reporting status for those. NOTE: Meta's `campaign_and_resource_get` ad lists are truncated by huge historical ad rosters (max_rows cuts the active ads), so do NOT switch Meta to management — reporting is better there. Snap has NO management API (`Campaign management is not supported for SCM`).

### RULE 23 — "TOP PERFORMING ADS" TABLE MUST FILTER BY ACTIVE STATUS (all 3 platforms)

`renderTopAdsInner` (the "TOP PERFORMING ADS" section) and its nested `buildPlatAdsRows('tiktok'|'snap')` rank every ad with spend>0 in the window and originally applied NO active-status filter — so PAUSED ads that spent recently kept showing there, even though the per-geo ADS panels correctly hid them. This is a SEPARATE render path from the per-geo panels and was missed in earlier active-ads fixes. Fix: the Meta loop now calls `isAdActive(<name minus date/v/copy, geo kept>)` and skips inactive; `buildPlatAdsRows` has a `_platActive(name)` helper (TikTok→`TIKTOK_AD_STATUS` active-in-any-geo by ad number; Snap→`SNAP_AD_STATUS` active-in-any-geo by number) and skips inactive. Note `isTTAdActive`/`isSnapAdActive` are LOCAL to the platform panel builders and NOT in scope here, so the check reads the global status maps directly. Whenever asked "active ads wrong", check EVERY render path that lists ads — there are at least four: the 3 per-geo ADS panels AND this Top Performing table.

### RULE 22 — `GRANULAR.snap.adsets` (UAE/KSA/KU) DRIVES THE SNAP BUDGET-TREND CHART — refresh every ingest

The "BUDGET TREND — DAILY SPEND BY CAMPAIGN" chart for Snap reads `GRANULAR.snap.adsets["UAE"|"KSA"|"KU"]` (per `BUDGET_TREND_CONFIG.snap`, source:'adsets'), NOT `D.snap` and NOT `SNAP_GEO_SPLIT_DAILY`. It is a THIRD Snap store, separate from the two the ADS panel and account trend use. Every Snap ingest must append the new day to all three of UAE/KSA/KU here (entry `{d,spend,sv,conv,atc,roas,cpo}`, newest-first at index 0), using the per-geo squad totals (= `D.snap.{uae,ksa,ku}`). If you forget, the chart silently flatlines at the last date present while every other Snap view is current. Confirmed Jun 2026: chart stuck at Jun 17 while D.snap/split were at Jun 22; the gap also hid a real Jun 18 budget shift (UAE 150→200, KSA 350→300). `verify_ook.py` now includes `GRANULAR.snap.adsets` in the freshness table.

### RULE 18 — SNAP_GEO_SPLIT_DAILY IS THE AUTHORITATIVE SOURCE FOR THE SNAP ADS PANEL

**The trap:** The Snap ADS panel (Active Ads card by geo) does NOT read from `GRANULAR.snap.ads[name]` per-day arrays. It reads from `SNAP_GEO_SPLIT_DAILY`. Injecting correct Jun 17 entries into `GRANULAR.snap.ads` has zero effect on what the ADS panel renders — the panel will still show Jun 16 (or whatever the last date in `SNAP_GEO_SPLIT_DAILY` is).

**Confirmed case (Jun 18 2026):** After Snap GRANULAR.snap.ads was correctly updated through Jun 17, the ADS panel still showed Jun 16. Root cause: `SNAP_GEO_SPLIT_DAILY` had only been built through Jun 16. Adding Jun 17 entries to `SNAP_GEO_SPLIT_DAILY` fixed the panel immediately.

**Two separate data stores for Snap — always update BOTH:**

| Store | Used by | Must update |
|---|---|---|
| `GRANULAR.snap.ads[name][{d,spend,...}]` | Hover charts, Ad-level overview table | Every Snap ingest |
| `SNAP_GEO_SPLIT_DAILY["UAE/KSA/KU / QA / BH"][name][date]` | **Snap ADS panel (Active Ads card)** | **Every Snap ingest — mandatory, not optional** |

**How to update SNAP_GEO_SPLIT_DAILY for a new date (e.g. Jun 17):**
1. Pull per-(ad × squad) for that date: `fields=date,ad_name,ad_squad_name,ad_status,cost,conversion_purchases,conversion_purchases_value,conversion_add_cart_swipe_up`
2. Map squad names to geo labels: `UAE*`→`"UAE"`, `KSA*`→`"KSA"`, `KW*`/`QA*`/`BH*`→`"KU / QA / BH"`
3. For each geo label, for each ad in that geo on that date, insert `{spend, sv, conv, atc, roas, cpo, avgpv}` under `SNAP_GEO_SPLIT_DAILY[geo][makeSnapDn(name)][date]`
4. sv and avgpv are in AED — divide by 3.6725 to get USD if needed (confirm from field values)

**Verify:** After patching, the latest date in `SNAP_GEO_SPLIT_DAILY` must match the latest date in `D.snap` and in `GRANULAR.snap.ads`.

---

### RULE 19 — GOOGLE CAMPAIGN DAY SUB-ROWS: DATA IS NEWEST-FIRST, DO NOT REVERSE

**The structure:** Each Google campaign in `GRANULAR.google.campaigns[name].days` is an array stored with the **newest date first** (Jun 17 at index 0, Jun 11 at index 6 in a 7-day window). The render function `buildGoogleCampsHTML` iterates this array to produce day sub-rows.

**The bug (Jun 18 2026):** The render function had `[...(c.days||[])].reverse().forEach(...)` — a `.reverse()` call that was ADDED to fix ordering at some point, but INVERTED the already-correct order, causing oldest-first display (Jun 11 at top → Jun 17 at bottom).

**Fix:** Remove the `.reverse()`. The array is already newest-first; iterating it directly gives the correct latest-first display.

**Verification:** After any change to day sub-row rendering, confirm the first sub-row under a campaign shows the most recent date (e.g. Jun 17), not the oldest.

**Rule:** Never `.reverse()` the `c.days` array for Google campaigns. If days appear oldest-first in the UI, the fix is NOT to add `.reverse()` — it means the data array itself has been stored in the wrong order and THAT needs to be fixed at the data level.

---

### RULE 20 — META CATALOGUE IS TWO SEPARATE CAMPAIGNS: Catalogue_GCC + Catalogue_GCC_ADV+ (do NOT re-merge)

**Context (Jun 18 2026 launch):** Meta now runs TWO distinct catalogue campaigns in GCC, and the dashboard must keep them separate everywhere — never collapse them back into a single "Catalogue":
1. **`Catalogue_GCC`** — the original Retargeting/Prospecting catalogue. Ads Manager adset name: `GCC_Retargeting & Prospecting - catalogue`.
2. **`Catalogue_GCC_ADV+`** — a separate Advantage+ Shopping campaign that launched **Jun 18 2026**. Ads Manager adset name: `GCC_Adv+ - catalogue - JUN 2026`.

Both campaigns serve the SAME creatives (EN_All_Product / EN_Men / EN_Women / EN_All_Plus Size catalogue carousels), so they are distinguished by **adset name**, not creative name. The Adv+ campaign initially runs only the `EN_All_Product` carousel.

**Two parallel data stores must each carry both, split by adset (NEVER double-count):**

A) **`GRANULAR.meta.adsets`** — TWO buckets:
   - `"Catalogue Retargeting / Prospecting - GCC"` → Retargeting/Prospecting adset only.
   - `"Catalogue Adv+ - GCC"` → Adv+ adset only (NEW key, created Jun 18).
   Per-ingest: pull `date,ad_set_name,cost,purchases,purchase_value,atc` filtered `ad_set_name =@ catalogue`; the row whose adset name contains `Adv+` (or `GCC_Adv+`) → `Catalogue Adv+ - GCC`; all other catalogue rows → `Catalogue Retargeting / Prospecting - GCC`. The two buckets' Jun-18-onward spend must sum to `D.meta.cat.spend` exactly (e.g. Jun 18: 668.97 + 108.85 = 777.82). Pre-Jun-18 history of the Retargeting bucket is already Retargeting-only — do NOT touch it.

B) **`GRANULAR.meta.ads`** — the Adv+ creative is a SEPARATE ad-level key:
   - Retargeting EN_All_Product → `EN_All_Product-page_catalogue_Static-Carousel_Catalogue` (existing key, Retargeting portion only).
   - Adv+ EN_All_Product → `EN_All_Product-page_catalogue_Static-Carousel_Adv+_Catalogue` (NEW key; the `_Adv+` token is REQUIRED for the geo-grouping split, see render note). Mark this key `active` in `META_AD_STATUS`.
   To split a combined EN_All_Product Jun-18 entry: pull per-ad×adset (`ad_name,ad_set_name,...`, filter `ad_set_name =@ catalogue`); Retargeting EN_All_Product = its own row; Adv+ EN_All_Product = the `GCC_Adv+` row. Catalogue ad-level Jun-18 sum (all `EN_*` keys not ending `_UK`) must == `D.meta.cat`.

**`D.meta.cat` is UNCHANGED by the split** — it remains the catalogue GEO total (both campaigns combined). The split lives only in the adset + ad-level breakdowns.

**Render wiring — the split must be reflected in ALL of these (re-merging any one re-breaks the view the user is looking at):**
1. `reRenderMetaAds` **GEO_GROUPS2** (ad-level section view): add `{ label:'Catalogue_GCC_ADV+', pattern:/_Adv\+/i }` **BEFORE** the catch-all `{ label:'Catalogue_GCC', pattern:/^EN_|^en_/ }`. Order matters — Adv+ must be tested first or the Adv+ key falls into the general catalogue group. All internal catalogue conditionals in this function use `geo.indexOf('Catalogue')===0` / `g.label.indexOf('Catalogue')===0` (NOT `=== 'Catalogue'`) so BOTH labels are treated as catalogue for campType, campOrder, multiType, and nameCT.
2. `metaAdsets` overview array (~L921): two rows — `name:'Catalogue_GCC'` (aggMetaGeo Retargeting bucket) + `name:'Catalogue_GCC_ADV+'` (aggMetaGeo Adv+ bucket).
3. second adset overview array (~L929): `geo:'Catalogue_GCC'` + `geo:'Catalogue_GCC_ADV+'` (aggAdset each bucket).
4. `BUDGET_TREND_CONFIG` meta series (~L961): two series keyed on the two adset buckets.
5. `META_CAMPS` (~L1016): TWO entries — `{ label:"Catalogue_GCC", adsets:["Catalogue Retargeting / Prospecting - GCC"], prefix:"CAT ·" }` and `{ label:"Catalogue_GCC_ADV+", adsets:["Catalogue Adv+ - GCC"], prefix:"CAT+ ·" }`. This drives the campaigns + ad-sets tables (each campaign shows its own adset(s) underneath).
6. sub-row label remap (~L1108): `.replace('Catalogue Adv+ - GCC','Catalogue Adv+')` alongside the existing `.replace('Catalogue Retargeting / Prospecting - GCC','Catalogue Ret/Pro')`.
7. **GEO MODEL — `GK`/`GL`/`GC` (~L844):** the Overview + Meta market-breakdown tables and the Spend-by-Platform matrix are GEO-keyed (NOT adset-keyed), so they need a third data store: a `catadv` GEO key.
   - `GK.meta` = `["uae","ksa","ku","uk","cat","catadv"]` (add `catadv`; do NOT add to tiktok/snap/google — only Meta runs Adv+).
   - `GL` = `…,cat:"Catalogue_GCC",catadv:"Catalogue_GCC_ADV+",…` (rename `cat`, add `catadv`). `GL.cat` is the SINGLE source of the catalogue label across every market-breakdown render (period-pill `buildMetaMBInner`, MTD/last7/last30/custom/single-day), so renaming it here renames it everywhere at once.
   - `GC` = add a 6th color (index 5) for `catadv` (e.g. `#0ea5e9`); colors are positional by index in `GK[pk]`.
8. **Spend-by-Platform matrix `MARKETS` array (~L978):** rename `{key:'cat', label:'Catalogue'}` → `label:'Catalogue_GCC'` and add `{key:'catadv', label:'Catalogue_GCC_ADV+'}`. The table auto-hides any market with no spend (`activeMkts` filter), so the Adv+ column only shows on date ranges that include Adv+ spend.
9. **`D.meta[date]` geo split (third data store, parallel to the adset + ad-level stores):** for each day Adv+ ran, `cat` carries Retargeting-only and a NEW `catadv` geo object carries Adv+. Jun 18: `cat={spend:668.97,sv:2900.9,conv:10,atc:70,…}`, `catadv={spend:108.85,sv:0,conv:0,atc:4,roas:0,cpo:0}`. Days before Jun 18 have NO `catadv` key (render reads `r[g]||{}` → shows "—"). `D.meta.spend` (total) is UNCHANGED; the GK geo sum (uae+ksa+ku+uk+cat+catadv) + foll must still == `D.meta.spend`. NB: `buildMetaMBInner` allocates per-geo ATC by spend-share (it does NOT read `geo.atc`), so the displayed Adv+ ATC is an allocation, not the raw 4 — this is consistent with how all geo rows show ATC.

**THREE parallel data stores must all carry the split (A adsets, B ads, C geo). Pre-delivery check: catalogue is split in (1) ad-level section view, (2) campaigns/ad-sets tables, (3) Overview MARKET BREAKDOWN, (4) Overview SPEND BY PLATFORM & MARKET, (5) Meta-tab MARKET BREAKDOWN. Missing any one means the user sees a stale combined "Catalogue".**

**Active-bucket sum check (RULE re Meta adsets) now includes BOTH catalogue buckets:** UAE ALL + KSA ALL + KU ALL + UK ALL + Catalogue Retargeting/Prospecting + **Catalogue Adv+** + Followers == `D.meta.spend` within $0.02.

**If Adv+ ever pauses / a second Adv+ creative launches:** keep the bucket; add the new creative as another `_Adv+_Catalogue` ad-level key (the `_Adv+` token routes it to the Adv+ section automatically). Never fold Adv+ spend back into the Retargeting bucket.

---

### RULE 21 — GOOGLE "BUDGET SHIFT DETECTION" WIDGET IS HIDDEN (user request, Jun 19 2026)

The Google tab's auto-detected "BUDGET SHIFT DETECTION — GOOGLE" card (≥15% sustained spend shift over ≥3 days, with EST. MONTHLY figures) is **hidden per user request**. The functions `detectGoogleBudgetShifts()` and `buildGoogleBudgetWidget()` are LEFT DEFINED (do not delete — avoids dead-reference risk); only the injection is disabled. The render call site (~L1013) reads:
`${pk === 'google' ? '' /* Budget Shift Detection widget hidden per request */ : ''}` (was `${pk === 'google' ? buildGoogleBudgetWidget() : ''}`).
Do NOT re-enable on future ingests. If the user later asks to bring it back, restore the `buildGoogleBudgetWidget()` call in that ternary.

---

### RULE 22 — SNAP ADS PANEL MUST NEVER DROP ACTIVE + DELIVERING ADS (user request, Jun 19 2026)

The Snap ADS panel is built from `SNAP_GEO_SPLIT_DAILY`, which is spend-derived — so an ad that is **ACTIVE / Delivering** but has **$0 spend and 0 impressions** (e.g. just-launched) produces no reporting rows in ANY Supermetrics pull (confirmed: cost AND impression pulls both return "No data" for such ads) and was silently dropped. That is unacceptable — active ads must always show.

**Mechanism:** `const SNAP_ALWAYS_ACTIVE = { "<geoLabel>": ["<cleaned dn>", …] }` declared right after `SNAP_GEO_SPLIT_DAILY`. After the `SNAP_GEO_SPLIT_DAILY` build loop in the panel builder, every dn in `SNAP_ALWAYS_ACTIVE[geo]` not already in `merged[geo]` is injected as `{spend:0,sv:0,conv:0,atc:0,wR:0}`. These render via `perfRowSignalOther` as a plain row — all metrics `—`, no signal tag (`_adSig` returns 'neutral' for spend≤0), sorted last by spend. Geo labels must match exactly: `"KSA"`, `"KU / QA / BH"`, `"UAE"`. An ad can be listed in multiple geos (multi-squad). First entry: `552_PlusSizes0626_Mn_Vid short_Vert_UGC VO` in KSA + KU/QA/BH (delivering, $0). Also added to `SNAP_AD_STATUS` as `"active"`.

**Every ingest:** pull `ad_name, ad_squad_name, ad_status, cost` (+`impressions`) for the latest day. For each ad with `ad_status == ACTIVE` whose geo (from `ad_squad_name`) has NO spend row in `SNAP_GEO_SPLIT_DAILY`, add it to `SNAP_ALWAYS_ACTIVE[geo]`. Once an ad starts spending it appears automatically from the split — REMOVE its `SNAP_ALWAYS_ACTIVE` entry then to avoid a duplicate. dn = ad_name with `_En_GLO…` and trailing geo/`_Snapchat_*` suffixes stripped (same cleaning as `makeSnapDn`).

---

### RULE 23 — PLATFORM-VIEW WIDGET ORDER: ROAS TREND + BUDGET TREND ALWAYS LAST (user request, Jun 19 2026)

In every platform view (Meta/TikTok/Snap/Google), the **ROAS Trend** chart and the **Budget Trend** chart render at the END, after the market breakdown and all ads/campaign tables. Order: KPIs → Market Breakdown → ads/campaign tables (+ Meta Followers) → ROAS Trend → Budget Trend. Implemented in all three view functions: `renderPlat` (single-day, default), `renderPlatRange` (custom range), `renderPlatMTD` (MTD). The budget-trend card is now built for ALL platforms at the view level (`const btCard = BUDGET_TREND_CONFIG[pk] ? buildBudgetTrendCard(pk) : null;`) — it was REMOVED from `renderGranularOther` (which used to inject it above the tables) to avoid duplication. Budget Trend default range = `'30'` (RULE: 30D default, see session log). Do not move these widgets back above the tables.

---

### RULE 24b — META MARKET-BREAKDOWN ATC USES TRUE PER-GEO VALUES WHEN AVAILABLE (Jun 19 2026)

`buildMetaMBInner` (Meta-tab market breakdown, all period pills) now reads the TRUE per-geo `atc` stored in `D.meta[date][geo].atc` instead of allocating the day-total ATC by spend share. Logic: `gr.map` accumulates `at+=geo.atc||0`; `useTrueAtc = totAtc>0 && |geoAtcSum−totAtc| ≤ max(2, totAtc*0.03)`; when true, `gAtc = round(g.atc)`, else falls back to the old spend-allocation (for older ranges lacking per-geo atc — 46 pre-Jun-11 days). This fixed Adv+ showing ATC 8 (allocated) vs 4 (true). NOTE: the 6 OVERVIEW-tab market breakdowns still spend-allocate ATC — extend the same fix there if the user asks.

---
Check each file matches the expected date before processing:
- TikTok: filename contains date range
- Snap: timestamp in filename
- Meta: `Reporting starts` / `Reporting ends` columns
- Google: header row date range (row 2 after skipping)

Flag mismatch → wait for confirmation.

---

## STEP 1 — Read Files

| Platform | Format | Encoding | Key col |
|---|---|---|---|
| Meta | CSV | UTF-8 | `Amount spent (USD)` |
| TikTok | XLSX | — | `Cost` (AED) |
| Snap | XLSX | — | `Amount Spent` (USD) |
| Google | CSV | **UTF-16, tab-sep, skip 2 rows** | `Cost` (AED) |

---

## STEP 2 — Currency

| Platform | Rule |
|---|---|
| TikTok | ÷ 3.67 |
| Google | ÷ 3.67 |
| Meta | Use as-is (USD already) |
| Snap | Use as-is (USD already) |

---

## STEP 3 — Geo Detection
Check Ad Name first → fall back to Ad Set / Ad Group name.

| Key | Patterns |
|---|---|
| `uae` | `UAE`, `_UAE_` |
| `ksa` | `KSA`, `_KSA_` |
| `ku` | `Ku & Qa`, `KW/QA/BH`, `KUW`, `QAT`, `KWT`, `Ku/Qa/Bh` |
| `cat` | `Catalogue`, `Catalog`, `Retarget`, `GCC` |
| `followers` | `Brand-Social-Followers`, `Brand`, `Awareness` (Meta only) |

**Snap KU special:** KU ads often have NO geo in Ad Name — must check `Ad Set Name` for `KW/QA/BH`.

---

## STEP 4 — Platform Processing

### TIKTOK
- Filter: `Primary status == 'Active'` rows only
- Spend: `Cost` ÷ 3.67 | SV: `Purchase value (website)` ÷ 3.67
- Conv: `Purchases (website)` | ATC: `Adds to cart (website)`
- Geo from Ad Name → Ad Group name

### SNAP
- Filter: Active ads only
- Spend/SV already USD: `Amount Spent`, `Purchases Value`, `Purchases`, `Adds To Cart`
- Geo from Ad Name → Ad Set Name (check Ad Set for `KW/QA/BH`)
- **Snap export scope varies** — sometimes full-account (all 12 ads UAE+KSA+KU in one file, e.g. Apr 16), sometimes UAE-only (4 ads). Always check the row count and Ad Set Names to determine scope before processing.
- When single-file full-account: process all ads in one pass. When multi-file (UAE + separate KSA/KU files): combine before computing totals.
- Same ad name can appear in multiple geos (e.g. `279_Spring0325_...` runs in both KSA and KU). Use `(name, geo)` as the unique dedup key — NEVER just `name`, or you'll collapse rows and lose spend.
- **Active Ads card is per-geo and a creative runs in several geo squads at once → regenerate `SNAP_GEO_SPLIT_DAILY` every ingest (RULE 16).** Pull per-`ad_squad_name`, split each ad's file daily totals across its geos by spend share. Skipping this makes KU/QA/BH (and others) drop active ads.

### META
See `references/meta.md`. Key points:
- Separate Followers rows before any calculation
- `D.meta.spend` = sales + followers total
- `D.meta.roas` = sales_sv ÷ total_spend
- Geo `spend` = sales-only spend per geo

### GOOGLE
See `references/google.md`. Always use highest of 3 SV methods.

**CRITICAL filter**: `g = g[g['Campaign status'] == 'Enabled']`. The CSV includes 8+ total/summary rows (`Total: Campaigns`, `Total: Account`, `Total: Performance Max`, `Total: Search`, `Total: Shopping`, `Total: Demand Gen`, `Total: In-stream video`, `Total: Display`) which will DOUBLE the spend if not filtered. Filtering by `startswith('Total')` is fragile — use `Campaign status == 'Enabled'` instead.

**GCC PMAX split**: `PMAX_UAE_KSA_KW_QA_Abaya_EN_goog` spans all 3 geos. Split its spend/conv/sv proportionally across UAE/KSA/KU using each geo's **SEM-only spend ratio** (SEM campaigns, not PMAX). Example Apr 16: SEM totals UAE $127.79 / KSA $12.17 / KU $65.80 → UAE gets 62.11%, KSA 5.91%, KU 31.98% of the split campaign's $173.86.

**Conv rounding**: Per-geo conv values after split will be fractional. Round to nearest int while preserving the grand total. Apr 16: UAE 15.73→16, KSA 0.35→0, KU 1.92→2 (sum=18 ✓).

---

## STEP 5 — CPO Sanity Check

| Platform | Valid range |
|---|---|
| Meta | $30–$220 |
| TikTok | $50–$280 |
| Snap | $10–$95 |
| Google | $30–$180 |

CPO=0 with spend>$100 → wrong metric (ATC used instead of purchases). Fix before inserting.

---

## STEP 6 — Update D Object
Use JSON parse + re-serialize (see Rule 3). See `references/d-object-structure.md` for exact formats.

---

## STEP 7 — Update GRANULAR

### Key architecture — TikTok & Snap
- `seenDates` dedup across ALL keys (permanent + dated `_marXX`/`_aprXX`)
- Dated keys hold real daily uploaded data — **NEVER delete them**
- **NEVER create fake permanent keys** with invented data
- New ad = data only from the day it first appears in the export
- ATC must come from the export — never zero it out or invent it

### Snap GRANULAR specifics
- `SNAP_AD_STATUS` keys = base key after stripping `_marXX`/`_aprXX`/`_vN`
- `makeSnapDn` handles `UAE_Snap`/`UAE_Snapchat` (geo before platform) with special regex
- `perfRowSignalOther` always needs geo param `g.label` for `data-geo` hover filtering
- **`SNAP_GEO_SPLIT_DAILY`** (per-(ad×geo) last-7 split) drives the Active Ads card — rebuild it each Snap ingest and run RULE 16 asserts (per-ad totals preserved; per-geo == `D.snap.<geo>` minus paused). `SNAP_AD_GEO` values stay UPPERCASE.

### Meta GRANULAR adset keys (exact — 8 keys, verified Apr 16)
```
"UAE Abaya - ASC"
"KSA Abaya - ASC"
"KU Abaya - ASC"
"UAE Pyjama - ASC"
"KSA Pyjama - ASC"
"KU Pyjama - ASC"
"Catalogue Retargeting / Prospecting - GCC"
"Followers GCC - Brand"
```
Budgets were shifted Apr 7 (Abaya→Pyjama in UAE/KU) and Apr 16 (UAE Abaya $500/Pyjama $500, KSA Abaya $600/Pyjama $300, KU Abaya $200/Pyjama $450). Abaya and Pyjama are SEPARATE adset keys — the old "UAE Ongoing - ASC - En" combined key no longer exists.

### Meta Followers — per-country (ad-set) geo block (added Jun 4 2026)
The Followers campaign is **4 separate per-country ad sets**, not one GCC ad set:
```
Meta_OOK_UAE_Brand-Social-Followers_MF-Prospecting-Standard_FEB26        → uae
Meta_OOK_KSA_Brand-Social-Followers_MF-Prospecting-Standard_FEB26        → ksa
Meta_OOK_KUW-QAT-BH_Brand-Social-Followers_MF-Prospecting-Standard_FEB26 → ku
Meta_OOK_UK_Brand-Social-Followers_MF-Prospecting-Standard_MAY26         → uk   (UK started May 28 2026)
```
The dashboard still stores ONE daily record under `GRANULAR.meta.adsets["Followers GCC - Brand"]` (total `spend` + `conv`[=link clicks]), but each record now ALSO carries a `geo` block that powers the panel's **BY COUNTRY — AD SET** table:
```
{"d":"Jun 3","spend":135.7,"sv":0.0,"conv":1007,...,"geo":{"uae":{"spend":28.86,"lc":203},"ksa":{"spend":28.93,"lc":274},"ku":{"spend":29.83,"lc":376},"uk":{"spend":48.08,"lc":154}}}
```
**Build (every ingest):** pull `fields=date,adset_name,cost,action_link_click ; filter: campaign_name =@ Follower` for the target day(s). Map adset→geo (UAE/KSA/KUW-QAT-BH/UK); `spend=cost` (**Meta cost is already USD — do NOT divide by the AED rate**), `lc=action_link_click`. Emit only geos with spend that day (UK absent pre-May 28; whole campaign was paused Apr 28–May 17). **Assert per day:** `sum(geo.spend) == record.spend` (±$0.05) and `sum(geo.lc) == record.conv` — they MUST reconcile because the GCC total IS the sum of the 4 country ad sets. Panel renders spend / share-of-followers-spend / link clicks / CPC (=spend÷lc) per geo, summed over the selected range; rows with $0 in-range are hidden.

**ALSO MANDATORY every ingest — refresh `META_FOLLOWER_ADS` (the per-AD sub-rows).** The BY COUNTRY — AD SET table renders indented `↳` per-ad sub-rows **under each country**, fed by a SEPARATE top-level store `const META_FOLLOWER_ADS = {uae,ksa,ku,uk:{ adName:{ "Mon D":[spend,linkClicks] } }}` (declared ~L3669, JSON-parseable via brace-match). This store is NOT the same as the ad-set geo block above and is NOT auto-maintained by the geo-block step. If you only update the geo block, the country rows stay correct but **the per-ad sub-rows silently vanish for any view past the last date present in `META_FOLLOWER_ADS`** (the rows decay; from the client's view it looks like the breakdown was "removed"). Confirmed regression Jun 2026: geo block was current to Jun 21 but `META_FOLLOWER_ADS` stopped at Jun 18, so the Jun 21 Followers view showed the UK country row with no `↳` ad rows. To refresh: pull `fields=date,ad_name,adset_name,cost,action_link_click ; filter: campaign_name =@ Follower` for the target day(s), bucket each ad under its geo (UAE/KSA/KUW-QAT-BH→ku/UK→uk), and append `"Mon D":[cost, action_link_click]` to that ad's series (Meta cost already USD — do NOT divide by AED rate). **Assert per day & geo:** sum of per-ad `[spend,lc]` == the matching `geo` entry in the ad-set block (±$0.02 spend, exact lc). Followers ads the user keeps OFF (GCC) simply have no recent spend → no rows; only the live geo (currently UK: 418, 415) renders.

### Meta export — Ad Set names to GRANULAR key mapping
```python
def map_adset(ad_set_name):
    n = ad_set_name.upper()
    if 'CATALOG' in n: return 'Catalogue Retargeting / Prospecting - GCC'
    if 'FOLLOWERS' in n or 'BRAND-SOCIAL' in n: return 'Followers GCC - Brand'
    if 'UAE' in n and 'ABAYA' in n: return 'UAE Abaya - ASC'
    if 'UAE' in n and 'PYJAMA' in n: return 'UAE Pyjama - ASC'
    if 'KSA' in n and 'ABAYA' in n: return 'KSA Abaya - ASC'
    if 'KSA' in n and 'PYJAMA' in n: return 'KSA Pyjama - ASC'
    if ('KUW' in n or 'KW/QA' in n) and 'ABAYA' in n: return 'KU Abaya - ASC'
    if ('KUW' in n or 'KW/QA' in n) and 'PYJAMA' in n: return 'KU Pyjama - ASC'
```

---

## STEP 8 — Update ALL_DATES
```js
const ALL_DATES = ["Mar 1",...,"Apr 15","Apr 16"]; // append new date
```
Current tail: `...,"Apr 15","Apr 16"]`

---

## STEP 9 — Budget Change Markers (AUTO)
```js
{"date":"Apr 5","platform":"tiktok","direction":"up"}
```
Apply for all 4 platforms whenever spend changes meaningfully vs previous day.

---

## STEP 10 — Validate & Deliver

> ### 🚦 THE GATE: `verify_ook.py` is the single blocking pre-delivery check. PASS or do not ship.
> The recurring failure mode on this project is NOT structural corruption — it's a **display store that silently went stale** because one ingest step was skipped or shortcut (status maps from a single-day pull; `META_FOLLOWER_ADS` not refreshed; a geo split not rebuilt). These pass `node --check`, end in `</html>`, and reconcile at the account level — so prose checklists and "I remembered to update X" do NOT catch them. The only reliable safeguard is a machine that audits **every** store against the latest date.
>
> **`/mnt/user-data/outputs/verify_ook.py` (also kept in the repo) does this.** Run it as the LAST step before `present_files`, every single delivery, no exceptions:
> ```bash
> python3 verify_ook.py /mnt/user-data/outputs/ook.html
> ```
> It prints a freshness table (every store's latest date — any that isn't the latest day lights up `<<< STALE`), reconciles geo→account spend per platform, cross-checks `META_FOLLOWER_ADS` per-ad sums against the Followers country block, verifies the Meta active-adset sum, checks for duplicate dates, and sanity-checks the status maps (non-empty active set). Exit code 0 = `✅ PASS` = safe to ship. Exit 1 = `❌ FAIL` = **a panel is stale/broken; fix the named store and re-run. Do NOT call `present_files` on a FAIL.**
>
> **When a new display store is added** (a new adset bucket, a new platform, a new geo, a new derived map), ADD IT to `verify_ook.py`'s freshness list in the same session — an unaudited store is exactly how the next silent-decay bug ships. The script is the living checklist; keep it ahead of the dashboard, not behind it.
>
> This converts every known recurrence (stale status map, decayed followers rows, un-rebuilt snap split, geo≠account drift) from "ships silently, client catches it in a screenshot" into "blocks delivery on my machine." It does not catch brand-new bug *classes* — when one appears, fix it once, then add its check here so it can never recur silently.

> ### 📅 ALSO update `ALL_DATES` every ingest — it drives the DATE PICKER, separately from the data.
> `ALL_DATES = [...,"Jun 21","Jun 22"]` (~L405) is the array the date selector reads to know which days exist. It is NOT one of the data stores and is NOT touched by the D / GRANULAR patch steps. If you add a day's data but forget to append it here, **every store is fresh but the picker still caps at the previous day and defaults to it** — the client sees "still on yesterday" even though the new day is fully loaded. Confirmed regression Jun 2026 (Jun 22 data complete, picker stuck on Jun 21). Every ingest: append the new day's label to the END of `ALL_DATES` (chronological, comma-separated, exact `"Mon D"` format). `verify_ook.py` now asserts `ALL_DATES[-1] == LATEST` and FAILS if not — but append it as part of the day-add, don't rely on the gate to remind you.

Full pre-delivery checklist (the above gate automates most of this; keep for reference):
```python
# 1. D object parses
json.loads(content[i:d_end])

# 2. TARGET spend in D matches each platform's per-ad export total
for pk in ['meta','tiktok','snap','google']:
    for rec in d_obj[pk]:
        if rec['d'] == new_date:
            assert abs(rec['spend'] - expected[pk]) < 0.01

# 3. File ends cleanly
assert content.rstrip().splitlines()[-1].strip() == '</html>'

# 4. No multi-commas anywhere
assert not re.search(r',{2,}', content)

# 5. node --check on extracted script block
s = content.find('<script>')
e = content.rfind('</script>')  # rfind not find!
with open('/tmp/eval_test.js','w') as f:
    f.write('(function(){\n' + content[s+8:e] + '\n})();')
# subprocess: node --check /tmp/eval_test.js → returncode 0

# 6. ALL_DATES tail includes new date
# 7. GRANULAR has TARGET entries (should be ~70+ across meta/tiktok/snap/google ads)
# 8. SNAP_AD_STATUS sanity: each new key's base name present and "active"

# 9. ACCOUNT-LEVEL RECONCILIATION (RULE 10) — fire date-only query per platform on TARGET
#    and confirm per-ad sum matches account-level within tolerance.
#    If drift detected, re-pull and patch D + GRANULAR for that day before delivering.
for pk in ['meta','tiktok','snap','google']:
    account = pull_account_level(pk, target)
    assert abs(account['spend_usd'] - d_obj[pk][-1]['spend']) < 5.0
    assert abs(account['conv'] - d_obj[pk][-1]['conv']) <= 1
    # Snap ATC: tolerance 5 (unattributed events expected)

# 10. RENDER TRIPLET CHECK (RULE 9) — three coupled lines must list same geos:
import re
pat = r"(geo|adGeo|g\.label)===['\"](UAE|KSA|KU / QA / BH|Catalogue)['\"]"
hits = [(m.group(1), m.group(2)) for m in re.finditer(pat, content)]
# Each of geo, adGeo, g.label should reference UAE+KSA+KU (3 each = 9 total minimum
# in the ALL branch, plus Catalogue handling). Run `grep -n` and eyeball if uncertain.

# 11. ACTIVE META ADSET BUCKETS REFERENCED — verify each bucket with TARGET spend > 0
#     in GRANULAR.meta.adsets is referenced ≥2x in render code (RULE 13 from prior sessions).

# 12. BACKFILL DRIFT CHECK (RULE 11) — re-pull past 7 days account-level per platform
#     and patch any drift in D + GRANULAR before delivering.
for pk in ['meta','tiktok','snap','google']:
    history = pull_account_level_range(pk, target - 7, target)
    for day, row in history.items():
        d_entry = next((e for e in d_obj[pk] if e['d']==day), None)
        if not d_entry: continue
        if abs(row['spend_usd'] - d_entry['spend']) > 0.10 \
           or row['conv'] != d_entry['conv'] \
           or abs(row['sv_usd'] - d_entry['sv']) > 2.0:
            patch_day(pk, day, row)  # re-pull per-ad and patch D + GRANULAR

# 13. PRE-DELIVERY LIVE STATUS CHECK (RULE 12) — per-geo ACTIVE reconciliation.
#     DO NOT filter by cost — a paused $0-spend ad is invisible to cost>0 and
#     stays stale-active. Pull by ad_status == ACTIVE, scoped per geo, and set
#     the file's active set to EXACTLY the returned list (both directions).
# Meta: one pull per geo. filter: ad_set_name =@ <UAE|KSA|Ku> AND ad_status == ACTIVE
# TikTok: filter ad_status == AD_STATUS_DELIVERY_OK ; Snap: ad_status == ACTIVE
for pk in ['meta','tiktok','snap']:                  # google: no ad-level status
    live_active = pull_live_active_set(pk)           # by STATUS, not cost
    live_active -= followers_adset_ads               # user keeps Followers OFF
    dedupe_naming_variants(status_map[pk], live_active)  # Ku_Qa vs Ku&Qat, spaces
    for ad in list(status_map[pk]):
        status_map[pk][ad] = 'active' if ad in live_active else 'inactive'
    for ad in live_active:                           # missing-active → add
        status_map[pk].setdefault(ad, 'active')
```
Copy to `/mnt/user-data/outputs/index.html` (or `ook.html` per current convention) and call `present_files`.

### STEP 0.3b — Account-level cross-check (per RULE 10)

Run this **during ingest**, not just at validate-time, so attribution drift is caught before any GRANULAR mutation work is wasted.

After per-ad/per-campaign queries return, fire one extra date-only query per platform for TARGET. Compare:

| Platform | Per-ad sum | Account-level | Tolerance |
|---|---|---|---|
| Meta | sum cost across all rows | account `cost` (USD) | $5 spend, 1 conv |
| TikTok | sum cost_usd (DELIVERY_OK rows) | account `cost_usd` | $5 spend, 1 conv |
| Snap | sum spend ACTIVE rows | account `spend` | $5 spend, 1 conv, 5 ATC |
| Google | sum cost_usd campaigns | account `Cost_usd` | $5 spend, 1 conv |

If a platform fails: re-pull per-ad/per-campaign data fresh (the older pull is stale), recompute D entry, patch GRANULAR ads/adsets/campaigns for that day. Patch META_KU_COUNTRY too if Meta drifted.

---

## DASHBOARD JS ARCHITECTURE

### Three render functions — ALL must be updated for any UI change:
| Function | When called |
|---|---|
| `renderPlat(pk, d)` | Single day selected |
| `renderPlatRange(pk, rd)` | Date range selected |
| `renderPlatMTD(pk)` | MTD button active |

### KPI boxes
- `g6` CSS class = 6 boxes: ROAS · SPEND · SALES VALUE · SALES · ATC · CPO
- `g5` CSS class = 5 boxes: Google only (no ATC)
- Conditional: `...(pk!=='google'?[{l:"ATC",...}]:[])` in all 3 render functions

### MTD definition
- MTD = **current calendar month only** (Apr 1–Apr 4, NOT Mar 1–Apr 4)
- Filter: `r.d.startsWith(curMon)` where `curMon = last.replace(/ \d+$/, '')`
- `renderOverviewMTD` and `renderPlatMTD` must both apply this filter
- MTD pill label: `"MTD Apr 1 – Apr 4"`
- toggleMTD: `calPickStart = "${curMon} 1"`

### Hover graph cache
- `buildTTAdsHTML` and `buildSnapAdsHTML` reset cache at start: `window.XX_CACHE = {}`
- Cache populated from `dayAgg` inside breakdown loop (same source as table)
- Also populated in else-branch (breakdown hidden) using same dayRecs logic
- `getAdDailyData(baseName, geo, platform)` — platform param isolates each platform's data

### seenDates pattern (TikTok & Snap merged build)
```js
const ttSeenDates = {};
adNames.forEach(name => {
  if(!isTTAdActive(name)) return;
  const geo = detectTTGeo(name); if(!geo) return;
  const dn = makeTTDn(name);
  const seenKey = `${geo}||${dn}`;
  if(!ttSeenDates[seenKey]) ttSeenDates[seenKey] = new Set();
  const dailyRecs = ds.map(d => {
    if(ttSeenDates[seenKey].has(d)) return null;
    return (ads[name]||[]).find(x=>x.d===d)||null;
  }).filter(Boolean);
  if(dailyRecs.length > 0) {
    dailyRecs.forEach(r => ttSeenDates[seenKey].add(r.d));
    // aggregate and merge...
  }
});
```

---

## ACTIVE ADS REFERENCE (Apr 16, 2026)

### TikTok active ads (from Apr 16 export, 12 ads, $780.96 total)
- UAE: 515, 510, 511
- KSA: 515, 499, 497
- KU/QA/BH: 520, 515, 512
- GCC/Retargeting: 487, 486, 467

### Snap active ads (from Apr 16 export, 12 ads, $699.88 total)
- UAE: 493, 486, 515, 512  (note: 486 was "inactive" in STATUS — had to flip to active)
- KSA: 279, 487, 451, 510  (note: 279_Snap_KSA base was MISSING from STATUS — had to add)
- KU/QA/BH: 501, 502, 279, 508  (note: 279_Snap_KU was "inactive" — had to flip to active)

### Google campaigns (9 enabled, Apr 16 total $885.31)
- PMAX_KSA_Pyjama, PMAX_UAE_Pyjama, PMAX_UAE_KSA_KW_QA_Abaya (the GCC split)
- SEM_UAE_Generic/Brand/Abaya, SEM_KUW-QAT_Generic/Brand, SEM_KSA_Brand

### Meta active ads (Apr 16, 29 ads, $3110.61 total)
- UAE: 502, 506, 510, 511, 512, 513, 515, 516
- KSA: 499, 502, 506, 510, 512, 513, 514, 515
- KU: 498, 506, 510, 513, 514, 517, 518, 519
- Catalogue: EN_All, EN_Men, EN_Women (all _Catalogue suffix — different from old _Prospecting Catalogue variant)
- Followers: 4 adsets (UAE, KSA, KU, + UK from May 28 2026) — see STEP 7 Followers geo block
- Bare-name UAE ads (no Meta suffix): 515_Cp_GLO, 518_Cp_GLO

---


---

## GRANULAR STRUCTURE NOTES

### GRANULAR object top-level layout
```
const GRANULAR = {
  meta: { budgets:{...}, adsets:{...}, ads:{...} },
  tiktok: { adsets:{...}, ads:{...} },    // inside GRANULAR, not separate
  snap: { adsets:{...}, ads:{...} },
  google: { campaigns:{...} }
}
```
- `meta` section is at chars ~0 of GRANULAR body
- `tiktok` section found via `content.find('tiktok:{adsets:', 380000)`
- `snap` section found via `content.find('snap:{adsets:', 440000)`
- `google` section found via `content.find('google:{', snap_start)`
- `tiktok ads:{` found via `content.find('},ads:{', tt_start, snap_start)`
- `snap ads:{` found via `content.find('},ads:{', snap_start, google_start)`

### Snap GRANULAR: new daily keys (NOT appending to existing)
Each day's Snap data goes into a **new dated key** `_aprXX` (e.g. `_apr15`), never appended to a permanent key. Insert before the closing `}` of the snap `ads:{...}` block.

### TikTok GRANULAR: append to existing keys
TikTok daily data appends a new `{"d":"Apr 15",...}` entry to the existing permanent ad key array. Find the key, walk to array closing `]`, insert before it.

### TikTok ad name → GRANULAR key: FUZZY MATCHING REQUIRED
TikTok export ad names often **differ slightly** from the stored GRANULAR key (e.g. export says `..._Tiktok_UAE` but key is `..._Tiktok_UAE_Sales`, or export says `..._Tiktok_GCC_Retargeting` but key is `..._Tiktok_GCC_Retarge` — truncated). For 512 Ku there are two candidate keys (`_Ku/Qa/Bh_Sales` and `_Ku & Qa_Sales_ASC`) — pick the one with most recent data (check first entry's `d` field; later = more recently used). Build an explicit export→key map for today's ads rather than relying on exact match.

### Meta GRANULAR ads: 3-bucket insertion pattern
Each Meta ad from today's export falls into one of three buckets:
1. **Existing plain key** — ad name exists as-is in GRANULAR → prepend new `{"d":"Apr N",...}` as first array entry
2. **Append to existing `_apr13` (or earlier) dated key** — ad was introduced recently as a dated key and has since accumulated entries → find the dated key, prepend new entry to its array
3. **Brand new ad today** — create a new `{ad_name}_aprN` key with a single-entry array, insert before closing `}` of meta.ads block

Always verify total ads processed = total unique ad names in export, and sum of per-ad spends = export total spend. This catches bucket-assignment errors immediately.

### Snap STATUS map auto-fix check (CRITICAL)
After building Apr N Snap entries, for each new `_aprN` key compute `makeSnapDn` base name and verify it exists in `SNAP_AD_STATUS` as `"active"`. Three common problems:
- **Base name MISSING from STATUS** → ad won't render at all. ADD it as `active`.
- **Base name marked `inactive`** but spent money today → ad won't render. FLIP to `active`.
- **Duplicate entries** for same base name → duplicates can override each other. Scan for duplicates.

Example from Apr 16 session: `279_Snap_KSA` was missing entirely (added), `279_Snap_KU` was inactive (flipped), `486_Snap_UAE` was inactive (flipped). Without these fixes, 3 ads with real spend would not appear in the dashboard.

### JS syntax validation method
`node --check` does NOT work on `.html` files (ERR_UNKNOWN_FILE_EXTENSION). Instead:
```python
# Extract script block
s = content.find('<script>')
e = content.rfind('</script>')   # rfind not find — Chart.js CDN creates earlier match
with open('/tmp/eval_test.js','w') as f:
    f.write('(function(){\n' + content[s+8:e] + '\n})();')
# Run node — "document is not defined" = browser API only = CLEAN
# Any other error = real JS syntax problem
```

### Finding syntax errors in minified data blobs
Binary search within a single giant line using `node /tmp/snippet.js` on truncated prefixes with depth-aware closing braces. Track `{`/`}` depth char-by-char (respecting strings) to always close with the right number of `}`.

### Known past bugs to watch for
- Unquoted object keys: `{d:"Apr 13",...}` — all data keys must be quoted `{"d":"Apr 13",...}`
- Multiple commas: `}],,,,"key":` — caused by bad string insertion; always check for `re.finditer(r',{2,}', content)`
- Chart-axis FP artifacts: a tick `axisFmt` that appends a unit to the raw value renders floating-point noise like `2.8000000000000003x`. ROAS was `v=>`${v}x`` → fixed Jun 4 to `v=>(+(+v).toFixed(2))+"x"` (round to ≤2 dp, drop trailing zeros: 2.8x / 2.6x / 3x). **CPO has the identical latent bug (`axisFmt:v=>"$"+v`) — not yet fixed; use `v=>"$"+(+(+v).toFixed(2))` when it surfaces.** Metric configs live in the `roas/sv/sales/cpo` axisFmt block in `renderGranular` (~line 3377); the range/MTD trend charts also have `.toFixed(2)+'x'` tick callbacks (already clean).

## ★★ RULES 40–45 — added Sep 4 2026 (learnings from the Aug month-end + TikTok/Snap status session) ★★

**RULE 40 (MONTH-END FULL RECONCILIATION — the 7-day drift window is NOT enough):** RULE 11 only re-pulls the last ~7 days, but attribution matures FAR beyond that — Google PMAX trues up for weeks, TikTok has a 28-day click window, Snap 7-day, and Meta's tiny daily spend noise accumulates. So a full month's totals drift out of sync even though every recent day ties. **At each month close, or whenever the client checks a monthly ("Last month") total, do a FULL-MONTH reconciliation:** pull account date-broken (date, cost, conv, sv) for all 4 platforms across the whole month, diff every day vs the file, and true up EVERY drifted day (account + geo + adsets/campaigns), not just the last 7. Aug 2026 example of what had drifted beyond the window: Meta spend −$24 (accumulated noise), TikTok +2 conv/+$314 sv, Snap +6 conv/+$1,941 sv, Google +7 conv/+$2,524 sv. **Meta spend specifically:** the "sub-$1.50/day spend noise is within tolerance, leave it" rule is fine day-to-day but the residue accumulates to a visible monthly gap — at month-end re-pull and set every day's Meta spend to the exact Ads Manager value (conv/sv usually already match; it's spend-only). Method for TikTok/Snap/Google drifted days: set D account to the pull, then rescale geo + adsets/campaigns proportionally (largest-remainder for integer conv, direct scale for sv/spend) so everything still ties. **AED trap:** when diffing, Google & TikTok `sv` is AED (÷3.6725); Snap `sv` is USD-native. Converting Google's AED as if USD produced a fake +$270k "drift" — always convert before comparing.

**RULE 41 (A NEWLY-TURNED-ON AD NEEDS A $0 DATA ROW, not just an active status):** When Ibra activates an ad that hasn't delivered yet, setting it `active` in the STATUS map alone leaves it INVISIBLE — the ad-row render iterates DATA rows, so with no row it silently doesn't appear ("still missing 575"). Also seed a placeholder $0 row for the latest day:
- **TikTok:** add `{d:<latest>, spend:0, sv:0, conv:0, atc:0, roas:0, cpo:0, avgpv:0}` to `tiktok.ads` under the exact `<NAME>_Tiktok_<UAE|KSA|Ku/Qa/BH>_Sale` key.
- **Snap:** add the split-format display name `<NAME> [<KSA|KU|UAE> Sale]` to `SNAP_ALWAYS_ACTIVE[<geo label>]` (the built-in mechanism, purpose-made for just-launched $0 ads; the render force-creates a $0 merged row from it). Also add the num to `SNAP_GEO_ACTIVE[geo]`.
When the ad later delivers, the normal ingest fills real numbers into the same key/geo.

**RULE 42 (OFF-AD DISPLAY RULE — show paused ads only if they converted):** The ad-row render (TikTok + Snap) now shows: (a) ACTIVE ads always, even at $0; (b) PAUSED ads ONLY if they got a sale (`conv>0`) in the period, tagged a red **OFF** badge so their conversion stays visible; (c) paused non-converters (e.g. 574 UAE spend-but-0-sales) and dark Combo rows are HIDDEN. Filter is `.filter(r=>!r.off||r.agg.conv>0)`. In the merge loop, don't early-return on inactive — compute `active`, set `off=!active`, show if `active||hasData`, and mark `merged[geo][dn].off=false` if any contributing key is active. This also makes the shown rows reconcile toward the geo total for converting ads. Ibra's rule of thumb: a paused ad that still SOLD should show (tagged OFF); a paused ad that only spent should be hidden.

**RULE 43 (STATUS SOURCE OF TRUTH per platform — and the new Ads Manager "Status" column):** 
- **TikTok:** confirmed AGAIN Sep 4 — NO field anywhere reflects the real per-ad toggle. Reporting `ad_status`=`AD_STATUS_DELIVERY_OK` for all; Management API `campaign_and_resource_get` returns `status:"ENABLED"` for EVERY ad incl. the ones Ibra is turning off; delivery lies too. The ONLY truth is Ibra's Ads Manager **"Status" column** (the "New" feature) — he screenshots it per market. Carry forward last-confirmed set otherwise (RULE 39). Live campaign `1870266496222258`.
- **Meta & Snap:** the API `ad_status` / `ad_squad_status` IS reliable and is rebuilt each ingest — BUT it can LAG intraday when Ibra just toggled something (Sep 3–4: 572 Meta UAE still showed ACTIVE after he paused it; 575 Snap UAE was paused AM then switched back on). So Ibra's explicit correction/screenshot ALWAYS overrides the last pull, per (ad, geo).
- **When Ibra sends a per-market active list (any platform): set EXACTLY that set active for that geo and everything else inactive — add nothing from delivery.** Verify each geo against his screenshot by numbers.

**RULE 44 (AD-LABEL BUILDER — strip " Sale", render full KU/QA/BH):** The bracket geo label built by `makeTTDn` (and the Snap equiv) parses `_Tiktok_<geo>_Sale`, but the terminator only strips `_Sales` (with an s), so TikTok/Snap `_Sale` (singular) leaked in as "UAE Sale". Fix: `.replace(/\s+Sale$/i,'')` on the extracted geo. Also the old Ku chain's 3rd greedy replace clobbered "KU/QA/BH"→"KU/QA" and left bare "Ku" as "Ku" — replace the whole Ku chain with one rule: `.replace(/^Ku.*/i,'KU/QA/BH')`. NOTE: the Snap SPLIT-path render shows the raw split-key dn (`<name> [KU Sale]`) directly (not via makeSnapDn), so Snap labels still carry "Sale" — clean them at the split-dn display if Ibra asks.

**RULE 45 (PROVE RENDER FIXES BY RUNNING THE REAL FUNCTION):** When changing render logic, do NOT trust a Python re-implementation of the logic — EXTRACT the actual `buildTTAdsHTML` / `buildSnapAdsHTML` (+ its deps: makeTTDn/makeSnapDn, detectTTGeo/detectSnapGeo, aggRecords, perfRowSignalOther, _SIG/_adSig, and stub the fmt helpers + D/GRANULAR/STATUS maps) and RUN it in Node against the real data, then assert the produced HTML has the right ads shown, right OFF tags, and no unwanted rows. Several "it's fixed" claims this session needed re-checking because a simulation passed but the real render didn't (e.g. Combo showing as OFF; 575 KSA having no data row). Also: Ibra is often viewing the OLD deployed GitHub version — always tell him the md5 to commit.

## FILE BACKUP
If corruption occurs: `https://3rdscreen.github.io/ook-dashboard`

---

## SESSION LOG (most recent first)

### Jul 17 2026 — Jul 16 ingest + TWO stale-status catches (RULE 31 added, RULE 24a amended)
Ingested Jul 16, delivered, verify PASS, Δ=0.00 all four. Meta 2374.51/43/10180.3/376 · TikTok 606.28/11/11674.21/115 · Snap 800/9/1686.88/111 · Google 424.82/6/4437.6.
**Structural:** (a) NEW Meta creative `561_Newcolor0224 SS` in KSA — strong out of the gate ($176.73 → 3 conv / 1667 SV; KSA went to 6 ads). (b) NEW TikTok ad `227_B2B0125 SS` in KW/QA/BH. (c) **The followers campaign expanded UK-only → 4 geos** — the UAE/KSA/KU FEB26 adsets were switched back ON running ads `177_Allure1024 SS` and `522_Tank0426 SS`. `META_FOLLOWER_ADS` and the `Followers GCC - Brand` adset ALREADY supported 4 geos (they ran in May), so it slotted in with history intact — no restructuring. Followers Jul 16: UK 79.61/269lc, KU 7.39/75, UAE 7.69/35, KSA 6.64/44 = 101.33/423. **The KU followers adset threw 1 ATC** — that single ATC is what closes Meta's account total to 376 (per-ad geos sum 375); `META_GEO['foll']` MUST carry it or geo≠account. Verify now reconciles 8 followers geo-day cells (was 5).
**Then the user flagged two live/off mismatches within an hour — both real, and BOTH status sources were stale (→ RULE 31):**
- **Meta 487/KSA:** ingest pulled it ACTIVE (it did spend $11.31 on Jul 16); by afternoon a re-pull said PAUSED. Meta `adstatus` = status as of PULL TIME, not per-date. Re-pulled the FULL roster (cost filter, no ACTIVE filter) → only 487/KSA had changed; 20 others still ACTIVE. KSA 6→5 ads. 487 stays live in KU (per-geo pause).
- **TikTok 543/KW-QA-BH:** I initially pushed back because `campaign_and_resource_get` (RULE 24a's "source of truth") said ENABLED *and* reporting `ad_opt_status` said ENABLE/DELIVERY_OK — **both were wrong**. The user's screenshot was right. The tell was in TODAY's delivery: KW/QA/BH 397=$28.39, 227=$27.22, 487=$20.72, 489=$17.96, **543=$0/0 impressions**. Flatlined vs spending siblings = paused. 543 stayed live in UAE ($18.30) and KSA ($19.52) → flipped only the KU key. TikTok 13→12 active.
**Lesson (now RULE 31):** never argue against the user's Ads Manager screenshot using a status flag; verify with today's per-ad cost+impressions vs siblings. Also confirmed Meta UK is `CAMPAIGN_PAUSED` at campaign level (why UK went dark Jul 14) and Meta 543 is PAUSED in KU/UAE but ACTIVE in KSA.
**Also this session:** IG follows investigation — Ads Manager's "Instagram follows" (219, UK adset, 30d) is **NOT available via Supermetrics FA**: `field_discovery` for "follow" = 0 fields, and a full `ActionType` breakdown for that exact adset/window returned 35 action types with no follow among them (`action_like`/`action_subscribe` = null). Instagram Insights (IGI, account `17841450070923010` "One of a Kin") IS connected but is ACCOUNT-level organic only — 1,467 new followers over the same window vs 219 ad-attributed (~7x), no adset/geo dimension, so it CANNOT substitute. Left as-is pending user decision; flagged ~$20.30 cost per attributed follow.

### Jul 15 2026 — Jul 13 & Jul 14 ingests + hide-when-empty rule (RULE 30) + followers campaign rename
Ingested Jul 13 and Jul 14, both delivered, verify PASS, Δ=0.00 all four platforms. **Jul 13:** settled day, no new creatives/status; the paused MAR26 adsets finally aged out of the 7-day window so Meta per-ad == adset == account exactly (37 conv) — **first day since the cutover that RULE 26 did not apply**. Heavy RULE 11 backfill incl. TWO Google down-restatements (Jul 6 8→7, Jul 7 13→12). The double-487 fix held: backfilling the Snap split reported KSA 487 as a "miss" (the retired entry deleted per RULE 28) so it was correctly NOT re-added — expect and ignore that miss.
**Jul 14 — busiest structural day since the cutover:** (a) TWO new Meta creatives, `325 new_Spring0325 SS` (KU+UAE) and `547_Minimeabaya0526 SS` (UAE) → 3 new keys, marked active; (b) **Meta UK adset went to $0 with no impressions** — all 5 UK ads flipped inactive, UK panel now 0; (c) **three Meta ads spent but were NOT ACTIVE on the status pull** (543 KU, 543 UAE, 487 UAE) → flipped inactive per RULE 12 (status column of the latest day is the sole truth, spend≠active); every geo still exactly 5 ads, RULE 29 sweep clean; (d) **Snap 547 started delivering** in KU+KSA after sitting at $0 since Jul 9 (textbook RULE 27) while **489 went PAUSED in KU+KSA but stayed ACTIVE in UAE** → `SNAP_GEO_ACTIVE` now differs per geo (KU/KSA = 397/487/543/547, UAE = 397/487/489/543), still 4/geo. Meta active count is **20, not 22** — the 2 followers ads live in `META_FOLLOWER_ADS`, NOT in `META_AD_STATUS`; don't "fix" that. Google spend dropped to $315.72 (vs usual $460–490) — genuinely complete (Snap capped $799.82, Meta+TikTok full run-rate), flagged to user as a real drop, not a partial pull.
**Note on Snap `ad_status` semantics (learned here):** Snap's reporting API returns the CURRENT status repeated across every date row, not the historical status for that date — 489 shows PAUSED on Jul 9 rows yet spends Jul 10–14. So read it as "status as of pull time" and apply it to the LATEST day only (consistent with RULE 12); never infer that a row was paused on an old date.
**Requested changes (display-only, delivered same session):** added **RULE 30** (hide-when-empty / never delete — user: *"i dont want to delete it since now july 14 its off, but i need to see data of it when we pick other days that has data in it"*) applied to all 7 `gr` builders; and renamed the followers campaign labels to ALL Markets (data key untouched). Verified by simulation across Jul 14 / Jul 1–9 / Jun 18–25 / Jul 13 before delivering.

### Jul 13 2026 — Jul 11 & Jul 12 ingests (settled Sale_40%) + Snap KSA double-487 fix
Ingested Jul 11 and Jul 12, both clean and delivered (verify PASS). Structure fully settled: all three social platforms on Sale_40%, old TikTok/Snap ads fully off by Jul 11–12, no new creatives, no status changes. RULE 26 held both days (paused MAR26 adsets kept 1 late-attributing conv at $0 spend → Meta geo built from adset-level breakdown; per-ad sum trails account by the residual, reconciles exactly via adset-level). Maturation from the sale finally settled — Jul 12 had the lightest backfill in a week (Snap zero conv/SV drift). Completeness tell worked again: Meta ran a light $1,976 day on Jul 11 but Snap capped $800 + TikTok/Google full run-rate confirmed the day was complete (not partial), so published.
**Bug caught by user screenshot (Jul 13):** Snap KSA panel showed 5 ads not 4 — the retired retargeting `487_…UGCO VO [KSA]` and the active `487_…SS…[KSA Sale]` both rendered because `buildSnapAdsHTML` filters `SNAP_GEO_SPLIT_DAILY` by ad NUMBER, and both start with 487 (∈ `SNAP_GEO_ACTIVE.KSA`). The distinct `[KSA Sale]` display name I'd given the Sale row did not prevent the collision. Fixed by deleting the retired 487 entry from the KSA split (only collision in the whole file — 487 was the sole ad number reused across old retargeting + new Sale, and only ran KSA). Display-only, reconciliation untouched. Tightened RULE 28 with the concrete detection+fix (scan each geo for a number appearing in >1 split entry; delete the non-Sale one).

### Jul 11 2026 — Jul 5–10 daily ingests + the Sale_40% cutover (major, all delivered, verify PASS)
Ingested Jul 5,6,7,8,9,10 (each delivered). The big event: a **Sale_40%** adset launched in every country on all three social platforms, replacing the old geo adsets, with fresh creatives (544, 397SS, 489SS, 487SS, 543SS). Cutover TIMING differed by platform (→ RULE 27): **Meta flipped Jul 9** (launched + delivered same day — blockbuster 86 conv / 21,794 SV vs the usual ~20/5K); **TikTok & Snap** Sale squads were visible as $0 rows from ~Jul 3 but only DELIVERED **Jul 10**, so Jul 9 stayed on old ads for those two (also blockbuster on old creatives — the 40%-off landing pages converted hard). Jul 10 = clean Sale_40% on Meta + TikTok/Snap flipped over.
Four new rules from this week: **26** (paused-adset residual conv → pull adset-level geo breakdown, no cost filter; per-ad sum legitimately trails account), **27** (new adset sits at $0 for days before delivering — flip status only on cost>0), **28** (Sale_40% naming + where it lives per platform; TikTok Sale is a NEW campaign, not the old id; Snap squad names have a leading space and share ad numbers), **29** (phantom-active via `isAdActive` number/EN_ prefix fallback — stale keys render as dash rows; sweep + mark inactive; caught by a user screenshot showing KU = 7 not 5, and Catalogue = 9 not 4).
New catalogue creative **EN_Kids** added Jul 10. Meta geo built from the ADSET breakdown to capture MAR26 residual conversions (RULE 26). Heavy RULE 11 maturation all week (sale drove late attribution — e.g. Snap Jul 9 matured 17→23→ then 31 across pulls; TikTok Jul 9 26→31). Snap went OVER its $800 cap on Jul 10 ($839.95) when the new squad launched — **over-cap or full-cap = a complete day** (same tell as Meta full run-rate) when ingesting "today"; use it as the completeness gate before publishing a same-day pull. **Two mid-session CONTAINER RESETS** — recovered each time by re-`cp /mnt/user-data/outputs/ook.html work.html`, recreating the `dNN.py` data module from conversation context, and restoring `verify_ok.py` from `/mnt/project/`; the delivered `outputs/ook.html` always survives, so it is the recovery anchor. Also fixed 2 phantom KU keys + 5 stale catalogue `_Prospecting` variants (RULE 29) in a follow-up after Jul 9.

### Jun 19 2026 — Jun 18 daily ingest (clean, one verification catch)
Standard full ingest Jun 17 → Jun 18 across all 4 platforms. Patched in order: D (all 4 lists → 110 entries), ALL_DATES, meta.ads (26 Jun 18 prepends incl. new `EN_All_Plus Size…Catalogue` key; Catalogue GCC_Adv+ + GCC_Retargeting combined into one `_Catalogue` key; UK catalogue separate `_Catalogue_UK`), meta.adsets (6 active buckets), tiktok.ads (15 Jun 17 replacements after KU maturation + 12 Jun 18 appends; per-ad SV confirmed stored in USD = AED÷3.6725, geo sums == D exact), google.campaigns (8 Jun 18 prepended newest-first, 8 Jun 15 replaced), SNAP_GEO_SPLIT_DAILY (rebuilt fresh Jun 12–18, active squads only — 548-KSA paused all 7 days so excluded → KSA shows 3 ads), META_KU_COUNTRY (Jun 18, country sum == D.meta.ku exact), META_FOLLOWER_ADS (415/418 UK only; GCC follower adsets off; pulled exact per-ad inline_link_clicks 36/160 rather than spend-share approximating), STATUS maps rebuilt (Meta 25 active, TikTok 12, Snap unchanged), Snap Jun 18 budget marker.

**Active-ad counts (RULE 12, all confirmed via Jun 18 ad_status pull):** Meta UAE 6 / KSA 6 / KU 5 / UK 4 / Cat 4; TikTok 4/4/4; Snap UAE 4 / KSA 3 / KU 4. UK catalogue placement (`EN_All_Product…_Catalogue_UK`) was PAUSED on Jun 18 → marked inactive (still renders with Jun 18 spend $10.78 but inactive badge).

**Verification catch (why STEP pre-delivery exists):** Pre-delivery account-level re-pull flagged Google Jun 18 mismatch — file had conv 9 / SV $4592.90, authoritative `conversions`/`conversionsvalue` pull returned conv 8 / 13271.5 AED ($3613.49). Spend matched ($345.43). Root cause: `PMAX_KSA_Pyjama` Jun 18 had been captured at conv 2 / 6543.91 AED during the working pull, then Google **restated it down** to conv 1 / 2948 AED by verification time (all other campaigns identical). This is the same Google late-restatement class as May 8 / Apr 30 — except this time it shrank, not grew. Fixed D total + KSA geo + the one campaign-day, re-reconciled (D total == geo sum == campaigns sum == 345.43/8/3613.75). Meta/TikTok/Snap all matched account-level on first check. **Lesson reaffirmed: never skip the latest-day account-level cross-check even when per-campaign data looks internally consistent — Google can move a single campaign between the working pull and delivery.**

**RULE 17 note (snap.ads vestigial duplicate — non-breaking, left as-is):** `GRANULAR.snap` still contains TWO `ads:{}` blocks (block1 @~677671 small/clean Jun12-17, block2 @~686311 large historical). Unlike the TikTok dup (which broke the panel), this one is harmless: the Snap ADS panel reads exclusively from `SNAP_GEO_SPLIT_DAILY` (RULE 18), so whichever `ads:{}` the browser resolves is never consumed for display. Decision: do NOT inject Snap data into `GRANULAR.snap.ads` and do NOT delete the 89KB block (deletion is pure regression risk for zero display benefit). Rebuild `SNAP_GEO_SPLIT_DAILY` each ingest instead. The RULE 17 dup-key SCAN still runs every delivery to catch any NEW (breaking) dup in meta/tiktok/google.

**Catalogue split into two campaigns (post-delivery, user-requested → RULE 20):** Meta launched a separate Advantage+ Shopping catalogue campaign Jun 18 (`GCC_Adv+ - catalogue - JUN 2026`, $108.85/0conv/0sv/4atc day one). User wanted it tracked as its own campaign, not folded into Retargeting/Prospecting. Split into `Catalogue_GCC` + `Catalogue_GCC_ADV+` across all Meta views: new `Catalogue Adv+ - GCC` adset bucket, new `EN_All_Product…_Adv+_Catalogue` ad-level key (marked active), and 6 render wirings (GEO_GROUPS2 with `_Adv+` matched before the `^EN_` catch-all + all catalogue conditionals switched to `startsWith('Catalogue')`; both adset-overview arrays; BUDGET_TREND_CONFIG; META_CAMPS as two campaign rows each with its own adset; sub-row remap). Then (next pushback) split at the GEO level too — `GK.meta` gained `catadv`, `GL.cat`→`Catalogue_GCC` + `GL.catadv`→`Catalogue_GCC_ADV+`, 6th `GC` color, spend-matrix `MARKETS` entry, and `D.meta[Jun18]` split into `cat`(668.97) + `catadv`(108.85) — this drove the Overview MARKET BREAKDOWN, Overview SPEND BY PLATFORM & MARKET, and the Meta-tab market breakdown. `D.meta.cat` GEO field is now Retargeting-only (was combined); `D.meta.spend` total unchanged; three parallel data stores (adsets/ads/geo) all carry the split. Full procedure in RULE 20 — future ingests MUST keep all three separated and never re-merge.

**Google "Budget Shift Detection" widget hidden (user request → RULE 21):** disabled the Google-tab auto-detection card via the injection ternary (`pk==='google' ? '' : ''`); functions left defined. Do not re-enable.

### Jun 18 2026 (PM) — Three new rules from today's bug session

**Bug 1 — Snap ADS panel showing Jun 16 instead of Jun 17 (RULE 18)**
After GRANULAR.snap.ads was updated through Jun 17, the Snap ADS panel (Active Ads by geo) still showed Jun 16. Root cause: `SNAP_GEO_SPLIT_DAILY` had only been built through Jun 16. The ADS panel exclusively reads from `SNAP_GEO_SPLIT_DAILY` — not from `GRANULAR.snap.ads`. Fix: rebuilt `SNAP_GEO_SPLIT_DAILY` through Jun 17 using per-(ad × squad) pull. New RULE 18: these are TWO SEPARATE data stores; both must be updated on every Snap ingest. See RULE 18 for the full update procedure.

**Bug 2 — TikTok ADS panel showing Jun 16 instead of Jun 17, despite correct data in file (RULE 17)**
After full Jun 17 GRANULAR injection for TikTok, ADS panel still showed Jun 16. Python inspection showed all 15 ad keys with correct Jun 17 data. But the actual browser rendered Apr/May data. Root cause: a second stale `ads:{...}` block (80KB, Apr/May data only) was sitting inside `GRANULAR.tiktok` immediately after the correct first `ads:{}` block. JavaScript's duplicate-key rule silently used the LAST occurrence (stale). `node --check` passed. Python `content.find('ads:{')` found the first (correct) block and missed the second entirely. Only `eval()` of the actual JS string revealed what the browser saw. Fix: located both blocks by byte offset, deleted the 80KB stale second block. New RULE 17: after ANY GRANULAR injection, scan the platform section for duplicate top-level keys.

**Bug 3 — Google campaign day sub-rows showing oldest-first (RULE 19)**
Google CAMPAIGNS card showed Jun 11 at top → Jun 17 at bottom. The render function had `.reverse()` on the days array — but the array is already stored newest-first, so `.reverse()` inverted it. Fix: remove `.reverse()`. New RULE 19: Google days arrays are newest-first; do not reverse them.

**Also fixed today:**
- 548_KSA set inactive in TikTok (confirmed not running Jun 17 per AM verification)
- File path references corrected throughout: source is `/mnt/project/ook.html`, working copy is `/home/claude/work.html`, output is `/mnt/user-data/outputs/ook.html` (never `index.html`)

### Jun 18 2026 — RULE 12 hardened: 7-day active-ad check + missing-new-ads pattern
**Problem:** User sent AM screenshot showing 6 active ads in Meta UAE; dashboard showed only 2 (513 + 527). Root cause: 4 brand-new ads (549_Abaya0126_Wm, 550_Minime0526_Fm_Static, 552_PlusSizes0626_Mn, 553_PlusSizes0626_Wm) launched during the week had ZERO entries in `META_AD_STATUS` → `isAdActive()` hit the unknown→false branch → invisible in every geo. A separate stale-active was also found: 513 UAE had been incorrectly toggled inactive in a prior session (reverted to active — AM confirmed it's spending $156/day).

**Fix:** Per-geo ACTIVE pull with `last_7_days` + `campaignobjective != OUTCOME_TRAFFIC` returned all 6 UAE actives in one shot. Followed up with adset pull to confirm which geos each new ad runs in (549: UAE only; 550: UAE+KSA+UK; 552: UAE+KSA+KU; 553: UAE+KSA+KU). Added 10 geo-suffixed STATUS entries.

**RULE 12 hardened with 5-step mandatory checklist** — see RULE 12 above. Key additions:
1. Always pull `last_7_days` (not today-only) — catches ads launched mid-week
2. Check BOTH directions: stale-active AND missing-active
3. Verify per-geo KU country breakdown
4. Cross-check breakdown data last 7 days + last 3 days (RULE 11 overlap)
5. State active-ad count per geo explicitly before delivery

**Also noted for tomorrow's ingest:** New Meta campaign `Catalogue_GCC_ADV+` (Catalogue ADV+ for GCC) launched. New bucket **"Catalogue - ADV+"** to be added under Meta Catalogue section with ad `EN_All_Product-page_catalogue_Static-Carousel_Catalogue`. Confirm at ingest whether this ad should be removed from the existing Catalogue bucket or kept in both (it may run in multiple campaigns simultaneously).

### Jun 16 2026 — Google campaigns grouped by country in both render tables → RULE 15
**User request (cosmetic/UX):** Google campaigns were scattered — sorted spend-desc in the CAMPAIGNS card and raw object-key order in the OVERALL PERFORMANCE BY CAMPAIGN overview — so the same country's rows weren't adjacent. Added a shared comparator (`_googCountryKey` + `_googSpendOf` + `_googCampCmp`, defined once above `buildGoogleCampsHTML`) that clusters by country (**KSA → UAE → KUW-QAT → other → multi-geo PMAX last**), PMAX before SEM within each, then spend-desc. Wired into all THREE Google sort sites: `buildGoogleCampsHTML` ×2 (all-time/MTD + Last 7/Last 3 day-breakdown) and the overview `gCamps` build. The overview rows carry spend under `.agg.spend` vs the card's `.spend`, so `_googSpendOf` reads either shape and one comparator serves both. Multi-geo `PMAX_UAE_KSA_KW_QA_Abaya_EN_goog` is tested first (`UAE_KSA`) so it lands in the all-geo bucket, not KSA/UAE. The Adset Overview table groups Google by geo (3 rows) — left untouched. Verified: 2× `rows.sort(_googCampCmp)` + 1× `gCamps…sort`, single helper defs, `node --check` on extracted script clean. No data touched. → **RULE 15.**

### Jun 4 2026 — Followers per-country breakdown + Meta KU bare-name ad fix → RULE 14 + ROAS axis fix
**1. Meta KU/QA/BH Ad-level view showed only 1 active ad (should be 4) → RULE 14.** The KU_ALL sales ad set's Jun-3 active ads were 541/542/543/545; only 542 rendered because it alone carried a `_Meta_Ku&Qat_Sales_ASC` token. 541/543/545 were stored under bare `<n>_..._En_GLO` keys → `detectGeo` null → dropped from every geo bucket. Re-keyed the bare entries with the KU suffix (scoped to the Meta `ads` byte-range; the same bare keys exist in other platform GRANULAR objects). **543 was a SHARED name** — KU-sales $5.31 + Followers (KSA $2.56 + KU $1.44) = $9.31 stored — so split it to KU-sales-only via an `adset_name =@ KUW-QAT-BH_ALL` pull; 541/545 were clean (rename only). Post-fix the 4 ads sum to `D.meta.ku` Jun 3 exactly (465.17 / 5 / 1843.57 / 57). → **RULE 14** codifies the geo-token-in-key requirement + the shared-name split + the next-ingest rule.
**2. Added Followers per-country (ad-set) breakdown** to the Meta Followers panel (user request: see UK / UAE / KSA / KU·QA·BH). Followers is 4 per-country ad sets (not one GCC set). Pulled `campaign_name =@ Follower` per-ad-set daily history and attached a `geo:{uae,ksa,ku,uk}{spend,lc}` block to all 75 Followers daily records; every day reconciles to the stored total spend + conv (link clicks). New panel table: **BY COUNTRY — AD SET** (spend / share / link clicks / CPC). UK present only from May 28; campaign paused Apr 28–May 17. See STEP 7 → "Meta Followers — per-country geo block".
**3. ROAS trend axis float artifact.** Y-axis ticks rendered `2.8000000000000003x` because `axisFmt:v=>`${v}x`` appended the raw float; fixed to `v=>(+(+v).toFixed(2))+"x"`. CPO trend has the identical latent bug (`v=>"$"+v`) — flagged to user, not yet fixed. Logged under Known Bugs.

### May 25–26 2026 — UK geo launch on Meta + 3-pass render-bug hunt → RULE 13
**Context:** Client launched a new Meta-only Sales campaign for the United Kingdom at $150/day (ad set `UK_ALL-ongoing-Prospecting-ASC_EN-MAY26`, 4 ads: 397/484/541/544 with `_En_UK`/`_En_ UK`/`_GLO_UK` suffixes). Same Meta ad account → auto-converts to USD, no GBP special-casing. UK rolls into the overall Meta + all-platform daily totals AND gets its own geo row (like UAE/KSA/KU). Day-1 (May 25): $38.15 / 1 conv / $87.01 / 2.28× (light — launched mid-day). TikTok/Snap/Google have NO UK.

**The bug (took 3 passes, each found only when the user screenshotted what was still missing):** a new geo's data insert is easy; the problem is the Meta tab has **multiple independent render paths each with their own hardcoded geo list.** Pass 1 wired `metaAdsets` ×2 + `META_CAMPS` + `BUDGET_TREND_CONFIG` ("the 4 places" from the old note) — UK still missing from Ad-level view. Pass 2 found the ads-level views use separate `GEO_GROUPS`/`GEO_GROUPS2` regex arrays with no UK pattern (`detectGeo2`→null→ad dropped) + `isAdActive` had no UK branch + campType ALL-group line excluded UK. Pass 3 (user screenshots of MTD / Last 7 / Last 30 still blank) found the **real** root cause for the Market Breakdown tables: all four breakdown tables (`buildMTDMarketTable`, Last-7, Last-30, and the range view) read their geo list from `const geos = GK[pk]` — and `GK.meta` was `["uae","ksa","ku","cat"]` with no `"uk"`. One-line fix drove all four. Also needed `GL` label + a 5th `GC` color.

**Mitigation: RULE 13 (new geo launch).** Documents the full 11-location checklist (GK/GL/GC, both metaAdsets, META_CAMPS, BUDGET_TREND_CONFIG, both GEO_GROUPS arrays, campType line, isAdActive) + Python verification that simulates each render path before delivery. Lesson: "the same geo list" lives in ≥4 conceptually separate components that don't share a source — trace the specific component the user points at, don't assume a prior edit covered it.

**Also this period:** May 18-24 RULE 11 backfill patched 9 drifts (TikTok May 23 matured 4→5; Snap May 20/22/24 grew; Google May 20/23/24 grew). RULE 12 per-geo live status held (Meta 20 active incl 4 UK ads; TikTok 8; Snap 11). TikTok May 21 SV still $0 (genuinely unmatured).

### May 14 2026 (PM) — Snap account-wide attribution window flipped to 7-day
**Context:** Until May 13, only the UAE Retargeting squad used 7-day click attribution; KSA and KW/QA/BH squads were on 28-day. The OOK pipeline used `1_DAY__28_DAY` for everything, which matched KSA + KU's settings and over-reported UAE squad slightly (UAE squad over-reported ~+0 conv net but specific days off by 1-2 conv; net $674 SV understated across May 1-13 due to platform reporting quirks).

**Starting May 14 ingest onward**: ALL Snap squads (UAE + KSA + KW/QA/BH) are on 7-day click attribution. Pipeline must use `1_DAY__7_DAY` going forward.

**Do NOT retroactively repatch May 1-13.** The file's existing numbers represent legitimate pull-time snapshots under the squads' settings at the time. Repatching would create more drift confusion than it solves; UAE-squad differences are within $674 net over 13 days.

**Critical**: The `attribution_window` setting in Supermetrics queries OVERRIDES per-squad Ads Manager settings — it forces all squads in the response to use the specified window. So under mixed-squad-attribution (pre-May 14), there's no clean way to pull "match each squad's native setting" in one query. From May 14 the squads are uniform, so `1_DAY__7_DAY` matches Ads Manager exactly for every squad.

### May 14 2026 — Two new rules forced by repeated drift + user pushback
1. **Backfill drift discovered at scale**: May 1-13 audit showed TikTok and Snap chronically understated by 1-7 days of late-attribution conversions. TikTok: 4/13 days drifted (+8 conv, +$1,934 SV). Snap: 6/13 days drifted (+19 conv, +$4,113 SV). Total $6K recovered across 27 hidden conversions. **Mitigation: RULE 11 (backfill drift check) — re-pull past 7 days on every platform before every delivery, patch any drift.**
2. **Active-ad status drift caught by user**: `Combo_En_GLO  _Meta_UAE_Sales_ASC` had $683 spend on May 13 then was paused. May 13 export said ACTIVE, current platform state was PAUSED. Dashboard's "Active ads" view would have shown a paused ad. **Mitigation: RULE 12 (pre-delivery live status check) — pull current ad_status from each platform with `cost > 0` filter, flip any paused-on-platform-but-active-in-file ads to inactive before delivery.**
3. **Confirmed B2B/wholesale pattern on Google SEM_UAE_Brand**: 3 consecutive days (May 10-12) of huge ROAS — $16,549 + $8,496 + $6,481 USD on $98 spend = 321× combined. Verified real-as-reported by account-level Google. By May 13 returned to normal ($337 SV / 12.9×).
4. **Whitespace variants in ad names**: Some Supermetrics queries normalize double-spaces to single-spaces depending on filter clause. When auditing RULE 12, use file's existing key spelling as canonical; do NOT add duplicate variants.

### May 8 2026 — Two bugs caught by user pushback
1. **Google attribution drift**: between first pull and verify pull (~30 min apart), `PMAX_UAE_Pyjama_EN_goog` gained 2 conv + $1,021 SV. First delivered Google: $767.56/10/$2828.07 → truth: $771.39/12/$3106.01. Same drift class as TikTok Apr 30. **Mitigation: RULE 10 + STEP 0.3b account-level cross-check now mandatory.**
2. **Meta ad-level render: KSA and KU/QA/BH disappeared.** First "fix" only updated line 1629 (input classifier). Lines 1681 (campOrder) and 1713 (day-row filter) still expected `['Abaya','Pyjama']` → `presentTypes=[]` → entire geo skipped. **Mitigation: RULE 9 (render triplet) — all three lines must be updated together.**
3. **Confirmed consolidation timeline:**
   - UAE → ALL on Apr 27 (Pyjama merged abaya in)
   - KU → ALL on Apr 28 (renamed in place)
   - KSA → ALL on May 7 (new bucket created, legacy Abaya/Pyjama frozen)
4. **TikTok ad-group rotation:** `KSA - May 26 - Interest 1.0 + iOS` is now the live KSA ad group; `KSA - Jan 26` paused. Same `KSA Interest - IOS` rollup bucket — no render code change needed.

### Apr 17 2026 — Prior session (snapshot of skill before this update)
See git history of `index.html` for granular context.

---

## REFERENCE FILES
- `references/meta.md` — Followers separation, geo, GRANULAR adset keys
- `references/google.md` — SV method selection, campaign filtering
- `references/d-object-structure.md` — Exact D object entry formats
- `references/historical-context.md` — Data pipeline, back-calc method, ROAS ranges

---

## RULE 41 — Catalogue model: `cat` vs `catnd` are SEPARATE additive geos (learned Sep 12 2026)

D.meta has TWO catalogue geo keys and they must never be merged:
- `cat` = Catalogue_GCC
- `catnd` = Catalogue_KSA National Day (live ~Sep 9 2026)

Account = uae + ksa + ku + uk + cat + catadv + foll + **catnd**. The `Catalogue Retargeting / Prospecting - GCC` adset bucket COMBINES the two (bucket.spend = cat.spend + catnd.spend); D keeps them split — never reconcile that bucket against `cat` alone. Render already supports it: `GK.meta=["uae","ksa","ku","uk","cat","catnd","catadv"]`, label `catnd:"Catalogue_KSA National Day"`. `verify_ook.py` GEOS['meta'] MUST include `catnd`.

**MISTAKE TO AVOID:** when the meta geo-sum falls short of the account total, do NOT inflate `cat` to close the gap. Check for a missing/under-counted `catnd` first — inflating cat double-counts against catnd and silently drops the National-Day catalogue from the split. KSA National Day splits three ways in Meta: sales prospecting → `ksa` (adset "KSA | National Day | Sep 2026"); catalogue → `catnd` (adset "KSA National Day - Catalog"). Old KSA_ALL ads go ADSET_PAUSED → inactive once National Day is live.

## RULE 42 — Every ad that ran on the newest day needs a newest-day row (learned Sep 12 2026)

A full daily ingest adds the newest-day entry to EVERY per-ad store whose ad ran — not just D geo + the adset bucket. **Catalogue creatives are the classic miss:** EN_Men / EN_All / EN_Women / EN_Plus Size / EN_Kids_Abaya (GCC) and EN_ALL_Catalog / EN_Women_Catalog (KSA National Day). Without a newest-day row they VANISH from the ADS panel the instant that day becomes the default view. Pre-delivery: for each geo, confirm every ACTIVE ad that ran has a newest-day entry under its correctly-named key; catalogue creatives must sum to D.meta.cat (GCC) and D.meta.catnd (KSA ND) exactly. New KSA National Day catalog creatives may be absent from META_AD_STATUS — add them as `active` so they render.

## RULE 43 — Ad-key hygiene: keys carry the full creative name (learned Sep 12 2026)

The ADS panel derives an ad's display name from its key: everything before `_Meta_<geo>_Sales_ASC`. A stripped key like `576_Meta_UAE_Sales_ASC` renders as a bare "576". Ad keys MUST be `<num>_<CreativeName>..._Meta_<geo>_Sales_ASC`, built from the pulled `ad_name`; never leave a number-only key. Fix a stripped key by renaming BOTH the meta.ads data key and the META_AD_STATUS key together — a single quoted-string replace of `"<oldkey>"` hits the `":[` (data) and `":"active"` (status) occurrences at once.

**Split-brain reminder:** when two keys share a leading number (e.g. 561_Newcolor inactive vs 561_KidsAbaya active), the newest-day entry must go under the ACTIVE variant matching the pulled `ad_name`, not the same-number inactive variant — otherwise the panel shows the ad OFF.

## RULE 44 — Meta status sync + Snap attribution (reinforced Sep 12 2026)

- Meta ad status IS reliable from reporting `ad_status` on the latest day — sync to it. Ads flip day-to-day (UAE 569/571 paused while 576/577 activated); do NOT carry forward a stale active set. A newer Ibra screenshot overrides any earlier active set for that geo, even within the same session.
- Snap attribution is now **28-day**: `settings={"action_report_time":"impression","attribution_window":"1_DAY__28_DAY"}` to match the Ads Manager recap standard (supersedes any 7-day instruction elsewhere in this doc).

## RULE 45 — "Refresh Creative" badge trigger criteria (Ibra-defined Sep 14 2026)

The ADS-panel creative-health flag. Flag an active creative **"Refresh Creative"** when ANY one of these holds; otherwise it carries the neutral **"Watch"** badge. Apply by rule — never hand-type the flag.

1. **CPA ≥ 2× target CPA**, at ≥ 2× the minimum spend threshold (shorthand: "2× CPA = 2× spend minimum").
2. **CTR < 0.5%** over ≥ 1,000 impressions.
3. **Frequency ≥ 3.5 AND CPA climbing.**
4. **CTR down ≥ 30%** sustained for 2 weeks.
5. **No spend in the last 72 hours.**

## RULE 46 — Reading active ads (THE SIMPLE LOGIC) + showing $0 active ads (Ibra, emphatic, Sep 15 2026)

**Which ads are active is simple — read the platform's own status column in the screenshot. Do NOT infer from spend or over-engineer.**

- **Snap:** "Delivery Status" column — **"Delivering" = active**, anything else = not.
- **TikTok:** "Status" column — **"Active" = ON**, **"Paused" = off**.
- **Meta:** status/Delivery column — "Active" = active, "Paused"/"Off" = inactive.

The screenshot's status column is ground truth: set exactly that set active, everything else inactive. That's the whole logic — apply it directly.

**Showing an active creative that has $0 spend so far** (new/just-toggled — both panels are spend-driven and drop them otherwise):
- **Snap:** add its display name to `SNAP_ALWAYS_ACTIVE[geoLabel]` ("UAE" / "KSA" / "KU / QA / BH"), using the split-key display format `NNN_<name truncated> [<Geo> Sale]` (match existing SNAP_GEO_SPLIT_DAILY key style, not the raw name).
- **TikTok:** add an empty-array key `"<full ad name>_Tiktok_<geo>_Sale":[]` to GRANULAR.tiktok.ads AND set it active in TIKTOK_AD_STATUS. The panel shows an ad when `active || hasData`, so an active empty key renders with dashes.
- GLO creatives (e.g. 556) run in several geos; `SNAP_AD_GEO` pins each name to ONE geo, so a GLO ad toggled on in a second geo needs this treatment for that geo.

**Status edits: edit in place.** Never insert a new status key for an ad that already has one — duplicate keys resolve last-wins and silently override your value. For same-number collisions (561_Newcolor vs 561_KidsAbaya), set status on the variant that actually ran / the screenshot names.

## RULE 47 — New-creative key hygiene: Snap split & TikTok display names (learned Sep 16 2026)

The ADS-panel display name always comes from the store key, so a new creative's key must carry its full current name. Three failure modes seen today:

1. **Snap split bare-number / missing-suffix keys.** When a new creative first gets spend and the build's name map lacks it, it's written as the bare number (`"588"`) or a full name without the ` [<Geo> Sale]` suffix (`"510_..._En_GLO"`) — the panel then shows "588". ALWAYS write Snap split keys as `<full creative name> [<Geo> Sale]` (Geo = UAE / KSA / KU). Keep the name map complete.
2. **Legacy placeholder keys** like `"583_Snap [KSA Sale]"` / `"573_Snap [KU Sale]"` from old ingests: when such an ad goes active, rename it to the full creative name.
3. **TikTok data-key without a status entry.** An ad can have a `GRANULAR.tiktok.ads` key but no `TIKTOK_AD_STATUS` entry (happened to 554) → shows OFF despite running. When activating, verify/add `"<full name>_Tiktok_<geo>_Sale":"active"`. Don't guard the add with a truncated-regex object check.

**Same-number collision (RULE 43 extends to TikTok/Snap):** the current creative can be stored under an OLD name for the same number — e.g. 556 KU lived under `"556_FINAL HOURS Abaya0126 SS_Wm..."`, so setting status by leading number hit the stale key and displayed the wrong name. When the pulled `ad_name` differs from the stored same-number key, RENAME the key (data + status together) to the current name.

## RULE 49 — Catalogue creatives: write to the ACTIVE key + freshness guard (blank-rows bug, Sep 16 2026)

**Root cause:** catalogue creatives have multiple historical key variants for the SAME ad — `_Catalogue`, `_Prospecting`, `_Adv+`, and old April duplicates (from re-uploads/renames). The daily ingest resolved each creative with `startswith("EN_All_Product-page…")` and took the FIRST match — which on Sep 12–15 hit the INACTIVE `_Prospecting` twin. The panel displays the ACTIVE `_Catalogue` key, so it had no data past Sep 11 and EN_All/EN_Men/EN_Women rendered all dashes, while the data sat on the hidden twin.

**Fix rule:** when ingesting a catalogue creative's daily row, resolve to the key META_AD_STATUS marks **active** (the displayed one), never just the first prefix match. If data already landed on the wrong twin, MOVE the entries onto the active key. Same collision class as RULE 43/47 — one creative, several key variants.

**Regression guard:** verify_ook.py now has a **"CATALOGUE ACTIVE-CREATIVE FRESHNESS"** check — every active catalogue creative must have a LATEST-day entry, else the build FAILS. The general freshness table only checked that SOME ad ran; this checks that EVERY active creative did, catching blank catalogue rows before delivery.

## RULE 51 — Same-number twin keys: activate only the running one, key by exact ad_name (recurring, Sep 21 2026)

A creative number frequently has **twin keys that are genuinely different ads**: SS (Static Story) vs video — `556_Abaya0126 SS_Wm` vs `556_Abaya0126_Wm` — or UGCO vs Details (499). Setting status by leading number activates **both**, so the panel shows a duplicate row (one with data, one blank). Ibra flagged this repeatedly.

**Fix rules:**
- When activating a status by number, activate ONLY the twin whose data key holds the **latest-day entry** (the running creative). Set all other same-number twins inactive. Never blanket-activate every number match.
- The ingest's mkey/tkey matches by number and can land the running creative's data on a **stale twin** (old SS/UGCO key). When Ibra sends the exact ad_name (always the first line of his message), **rename the data-bearing key (data + status together) to that exact name** so the panel displays it correctly.

**Regression guard:** verify_ook.py now has a **"DUPLICATE-ACTIVE COLLISION"** check — if two active Meta/TikTok keys share the same leading number within a geo, the build FAILS. This caught 499-UAE and 556-KU collisions that had already slipped through.

## RULE 53 — Meta: an off ad set turns ALL its ads off (Ibra, Sep 22 2026)

If a Meta **ad set** is paused/off, every ad inside it is implicitly **OFF** — do not add those ads as active even if the individual ad toggle shows on. Checking the ad-set level is easier than chasing each ad's toggle.

**Full Meta active logic (self-serve via MCP, no screenshots needed):** pull the **effective/delivery status**. Active or Learning = ON. Anything paused at ad, ad-set, or campaign level — `PAUSED` / `ADSET_PAUSED` / `CAMPAIGN_PAUSED` / not-delivering — = OFF. Prefer `effective_status` over the raw ad on/off toggle because it reports `ADSET_PAUSED` and thus captures the ad-set-off case automatically.

## RULE 54 — Snap active = "Delivering"; read it via MCP (Ibra, Sep 22 2026)

For Snapchat, active detection is simple: the **Delivery Status** column says **"Delivering"** = ACTIVE; anything else = off. No custom logic.

Self-serve via the Supermetrics MCP — pull the Snap ad delivery/status field each update and mark the Delivering ads active. Stop relying on Ibra's screenshots for Snap. **Self-serve status now applies to both Meta** (Active/Learning, RULES 52–53) **and Snap** (Delivering) — pull it, don't ask.

## RULE 55 — Always WRITE the pulled active sets every build; never skip on "unchanged" (571 miss, Sep 22 2026)

**Root cause:** the build judged Snap status "unchanged" from the pull and **skipped rewriting `SNAP_GEO_ACTIVE`**. The file's set was stale (571 had been dropped earlier); 571 toggled back ON for Sep 22, but the skipped write left it out. Assuming "unchanged" instead of writing what the pull returned is the bug.

**Fix rule:** EVERY build, always overwrite `SNAP_GEO_ACTIVE` (and Meta/TikTok status) with the freshly-pulled active sets. Writing is idempotent and free, and it's the only thing that catches an ad toggling back on. Never skip a status write because it "looks unchanged."

**Regression guard:** verify_ook.py now has a **"SNAP ACTIVE-SET COVERAGE"** check — if any Snap ad has latest-day split spend in a geo but isn't in `SNAP_GEO_ACTIVE`, it warns (review vs `ad_status`: a paused-but-spent ad is fine, a delivering one must be added). This surfaces dropped-but-delivering ads like 571.

## RULE 56 — TikTok's on/off toggle is NOT pullable via Supermetrics; confirm active sets with Ibra (Sep 23–27 2026)

TikTok's real toggle (`operation_status` / `material_operation_status`) is **incompatible** with ad-level fields in Supermetrics — every combination errors (`IllegalDimensionMetricCombinationException`). The only status pullable is **delivery** status (`ad_status = AD_STATUS_DELIVERY_OK`), which is not the toggle: it **misses** ads toggled ON with no spend yet, and **includes** ads paused-but-still-delivering. So a delivery-based TikTok active set is wrong exactly when toggles changed — which is why TikTok kept being wrong this session until Ibra sent the lists.

**Rule:** Meta and Snap active sets are self-serve from `ad_status` (RULE 52–54). **TikTok is not** — always confirm the TikTok active set per geo with Ibra rather than inferring from delivery. New TikTok creatives that clearly delivered can be added, but the full active/inactive set needs his confirmation.

## RULE 57 — Three build bugs recur on EVERY ingest; fix them at the source, don't rely on the guards (Sep 23/27/28 2026)

1. **Trailing comma on new empty keys.** Creating `"key":[]` then inserting `{entry},` before the `]` yields `[{entry},]` — valid JS (node passes) but invalid JSON (Python/verify FAILS). Fix: after any new-key insert run `c.replace('},]','}]').replace(',]',']')` before verify, or skip the trailing comma when the insert point is an empty `[]`.
2. **Stripped bare-number key for an ad entering a new geo.** When an ad starts running in a geo it wasn't in (484→UAE, 570→KU, 499→KSA), `mkey`/`tkey` finds no existing key and creates a stripped `484_Meta_UAE_Sales_ASC`. Fix: keep a full-name map for every ad that can appear in a new geo; create the key as `<full creative name><geo suffix>`, never bare number.
3. **Duplicate-active twin collision on status-apply.** Applying an active set BY NUMBER activates all same-number twins (SS / UGCO / Details) → collision every time. Fix: build the twin-resolution INTO the status-apply step (keep only the twin with latest-day data, or the clean non-SS/UGCO name, active), instead of letting the DUPLICATE-ACTIVE guard catch it post-hoc.

Also: the container can reset mid-session and wipe `/home/claude/work.html` — restore with `cp /mnt/user-data/outputs/ook.html /home/claude/work.html` (and `verify_ook.py` likewise) and carry on.

## RULE 58 — Seasonal campaign wind-down is a repeatable lifecycle (National Day, Sep 28 2026)

When a seasonal campaign ends, expect this sequence per platform: the ad **set** / ad **squad** flips to paused (Meta `effective_status = ADSET_PAUSED`; Snap `ad_squad_status = PAUSED`) → **all** its ads go off per RULE 53 even though they show residual spend → a **new prospecting ad set/squad** takes over with different creatives.

Steps to apply: (a) flip the old seasonal ads inactive; (b) activate the new prospecting ads (self-serve for Meta/Snap; confirm for TikTok); (c) rename the geo label from "X (National Day)" back to plain "X" in the render ternary (`g.label==='KSA'?'KSA':…`); (d) hide the dead seasonal catalogue by removing it from the platform's `GK` array (e.g. drop `catnd` from `GK.meta`). National Day Sep 2026 hit Meta + Snap + TikTok KSA exactly this way.

## RULE 59 — 3RDS Creative Decision Engine (per-ad verdict), Sep 30 2026

The per-ad hover card (`showAdHoverChart`) runs Ibra's **3RDS Creative Decision Engine** to output a verdict + a "Learning:" insight line. Ibra owns the logic and hands over updated versions; wire them in verbatim, only adapting inputs to what the dashboard actually has.

**Benchmarks (the knobs):** `ROAS_TARGET=3.0`, `CPO_TARGET=80` (ideal CPA), `CPO_MAX=100` (ceiling), `MIN_SPEND=100`, `MIN_IMPRESSIONS=1000`, `CTR_MIN=0.005` (0.5%), `FREQ_FATIGUE=3.5`, `NO_CONV_SPEND_LIMIT=150`.

**Verdicts:** ⚪ Watch — too early · 🔴 Stop / Refresh creative · 🔁 Refresh — fatigue detected · 🔁 Refresh hook / creative · 🟠 Investigate conversion — creative may be OK · 🚀 Scale budget · 🟢 Keep running · 🟡 Keep running — watch CPO · 🟡 Watch — recovering · 🔴 Expensive — review campaign · 🔁 Refresh / investigate · 🟡 Watch. `verdictClass` is derived from the emoji (🚀/🟢→ahc-keep green, 🔴/🔁→ahc-off red, else ahc-watch amber).

**Live inputs (data the dashboard has):** `avgRoas`, `recentRoas` (last 3 active days), `roasTrend`, `totSpend`, `totConv`, `totAtc`, `avgCpa` (=`cpo`), `recentCpa` (from the last-3 window; needs `r3Conv` added to the last3 loop). CPO-health tiers (good/acceptable/expensive/critical) and performance states (strong/profitable/recovering) run live.

**Dormant inputs — DO NOT fake them:** `impressions`, `avgCtr`/`recentCtr`, `ctrTrend`, `frequency` are NOT in the daily pulls. They're set to 0 and gated behind `hasImp=false` / `hasFreq=false`, so the branches that need them (`lowData` impressions clause, `lowCTR`, `ctrDeclining`, `fatigue`, `creativeProblem`, `conversionProblem`) stay dormant and the engine degrades cleanly to ROAS/CPA logic. The mislabeled `ctr` var elsewhere (`conv/atc`) is a checkout-rate proxy, NOT click CTR.

**To activate the creative-health half:** add **impressions + clicks** (→ real CTR) and **reach** (→ frequency = impressions/reach) to the daily Supermetrics pulls, populate `impressions`/`avgCtr`/`recentCtr`/`frequency`, and flip `hasImp`/`hasFreq` to `true`. These can only be captured going forward — no historical backfill.
