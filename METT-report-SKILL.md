---
name: METT-report
description: Build the METT hospitality performance dashboard for any METT property (Marbella, Singapore, Bodrum, Barcelona, Milan, etc.). Use whenever the user asks for a "METT report", "METT dashboard", "METT [property] dashboard", or provides Supermetrics account IDs (GA4, Meta Ads, Google Ads) for a METT hotel. Produces a single-file HTML dashboard with 7 tabs (Overview, Paid Media, Offers, Attribution, Booking Funnel, Markets, Creative), all wired to a date-range picker. Also covers **Deliverable B — `METT.html`**, the cross-property one-pager (all four hotels, month-filtered, spend/revenue/ROAS only) — use whenever the user asks for "one dashboard for all properties", "1 pager", or "METT.html". Pulls live data from Supermetrics, applies the chain-domain referral attribution model, and outputs a polished navy + dusty-rose dashboard branded as METT.
---

# METT Performance Dashboard — Build Skill

This skill produces single-file HTML for METT. There are **two distinct deliverables** — do not conflate them:

| | **A — Property report** | **B — Cross-property one-pager** |
|---|---|---|
| File | `METT_<Property>.html` | `METT.html` |
| Scope | one hotel, deep | all four hotels, shallow |
| Layout | 7 tabs, charts, creative grid | single page, one table per hotel |
| Filter | date-range picker (day granularity) | month segments |
| Chat | one chat per property | its own chat |
| Skeleton | `METT_Skeleton.html` (locked) | own layout, shared design tokens |

Everything below is Deliverable A unless it says otherwise. Deliverable B has its own section near the end.

For A: architecture, attribution model, and visual design are fixed. Only the data, currency, and property-specific copy change.

## When to use

The user provides three Supermetrics account IDs for a METT property:
- **GA4 property ID** (e.g. `327114117` for Marbella, `496938229` for Singapore)
- **Meta Ads account ID** (e.g. `act_1205759304496215` for Marbella, `act_2240093806419894` for Singapore)
- **Google Ads account ID** (e.g. `8964815527` for Marbella, `8360908539` for Singapore)

The user may write the Google Ads ID with dashes (`896-481-5527`); strip dashes for `accounts_discovery`, but use the dashed form in the dashboard footer.

## Currency rules — always

- **METT Marbella → EUR (€)**
- **METT Singapore → USD ($)** — see per-source note below
- **METT Bodrum → EUR (€)** (Turkey property, but client reports in EUR)
- **METT Barcelona → EUR (€)**
- **METT Milan → EUR (€)**
- **Yalikavak Marina, CASA METT Sitges** → confirm with user before building

For any new METT property, **ask the user which currency** before building. Default for European properties is EUR; default for non-Eurozone properties is USD with a note about the original currency.

### Singapore-specific currency note (verified May 2026)

The three Supermetrics sources for METT Singapore return values in **different native currencies**. Do NOT blanket-convert everything — that's a hand-me-down error from earlier sessions. Verified by reconciling live totals against existing array sums to the cent:

- **GA4 (`496938229`)** — `purchaseRevenue` is in **SGD**. Multiply by **0.7845** to get USD. (Spot-checked Mar 4: GA4 raw = 3,360 SGD → 3,360 × 0.7845 = 2,636 USD, matches stored array value 2,635.92.)
- **Meta Ads (`act_2240093806419894`)** — `cost` is already in **USD**. No conversion needed. (Verified Mar 1–Apr 30 array sum $3,641.84 matches live Supermetrics total.)
- **Google Ads (`8360908539`)** — `cost` is already in **USD**. No conversion needed. (Verified Mar 4 single-day cost 258.0591 matches array's 258.06 exactly; Mar 1–May 10 total $9,943.05 matches array sum + May increment to the cent.)

Locked SGD→USD rate: **1 SGD = 0.7845 USD**. Document the per-source currency in build-script comments so the next session doesn't redo the conversion. (See "Common errors & fixes" Lesson 24.)

### Bodrum-specific currency note (verified Jun 2026)

Opposite situation to Singapore: **all three** Supermetrics sources for METT Bodrum bill and report in **Turkish Lira (TRY)** — verified per source. The client reports in **EUR**, so **every** monetary value gets converted (this is the simple case — one rate, applied everywhere, no per-source split).

- **GA4 (`307945131`)** — `purchaseRevenue` in **TRY**.
- **Meta Ads (`act_797332184222785`)** — `cost` in **TRY**. ⚠️ **MULTI-BRAND ACCOUNT** — holds Folie Bodrum, Attiko, Isola, Moi Spa, Raise alongside METT. **Always** pull with `filters="adcampaign_name =@ METT Bodrum"`; the only METT campaigns are `METT Bodrum - Traffic (90,000TL)` (active) and `METT Bodrum - Engagement` (ended, no spend). (Note: METT Meta spend starts **Apr 1** — March is all zeros. Don't treat the leading zeros as a pull error.)
- **Google Ads (`2898288837`)** — `cost` and conversion value in **TRY**. (Google spend starts **Mar 9**; Mar 1–8 are zeros.)

Locked rate: **1 EUR = 53.5 TRY → 1 TRY = €0.018692** (EUR/TRY mid-market, verified 2 Jun 2026). Apply via a single `R = 1/53.5` constant.

**Reconciliation is the proof the rate + mapping are right** — but reconcile against the *correct scope*. For Bodrum (METT-only): channel-revenue sum = daily-revenue sum = ₺14,898,972 = **€278,485**; transactions = **113**; **METT** Meta ₺90,404 (€1,690) + Google ₺417,626 (€7,806) = **€9,496** paid spend. ⚠️ An account-level Meta pull gives ₺129,302 (€2,417) because it sweeps in Folie's ₺38,898 — that reconciles to itself but is WRONG (see Lesson 34). Always reconcile channel-revenue against the daily-array total AND confirm Meta spend is filtered to METT campaigns before trusting it.

### General SGD/EUR conversion checklist

If the GA4 property reports in a currency different from the dashboard currency (e.g. SGD → USD for Singapore), convert daily revenue arrays and all monetary values using a rate looked up via `web_search` (e.g. "SGD to USD exchange rate today"). Use today's rate, document it in the build script, and apply it to **every single one** of these locations:

1. Daily `ga4Revenue` array (the GA4-sourced one)
2. Daily `metaSpendArr` and `googleSpendArr` — **only if the ad platform reports in non-USD** (Singapore: Meta and Google are already USD, skip this step)
3. `BASELINE` constants (totalRevenue, paidRevenue, paidSpend)
4. All static HTML KPI values (Page I hero, Page II channel summary, Page IV attribution KPIs)
5. All `data-base="N"` attributes where `data-fmt="eur"` (the attribute name `eur` is a legacy label for "monetary" — kept for compatibility)
6. The visible cell text inside those `<td>` elements (NOT just the `data-base` attribute)
7. Every chart hardcoded number in the JS — Page I revenue-by-channel, Page II Google split donut, Page III offer charts (revenue/bookings/channel split/weekly trend) and offer funnel, Page IV attribution chart, Page V device chart, Page VI markets revenue chart
8. Creative cards array `revenue` and `spend` strings (Page VII)
9. Recommendation card text references in Page VIII (every `&euro;XXX` or `$XXX` literal) — note: Page VIII removed in May 2026; skip if absent
10. Top revenue creative KPI on Page VII
11. Page III KPI banner (Total offer revenue, Best offer, Cost per offer bkg)
12. Page III offers totals row
13. Page IV conversion path widget values
14. CPC values inside delta lines ("CTR X.XX% · CPC $0.XX")
15. `fmtEur()` and `fmtK()` helper functions in the JS (currency symbol)
16. All `setKpi('kpi-XXX', '<span class="cur">\u20AC</span>...')` calls — change `\u20AC` to the new currency symbol

**Exhaustive audit after conversion:** run `grep -c "&euro;\|€"` (or whichever symbol shouldn't be there). Result must be **0**. Skip this audit and you WILL ship a broken file.

## Workflow

### Step 1 — Verify all three accounts exist in Supermetrics

```
Supermetrics:accounts_discovery(ds_id="GAWA", filter="<GA4_ID>")
Supermetrics:accounts_discovery(ds_id="FA",   filter="<META_ID>")
Supermetrics:accounts_discovery(ds_id="AW",   filter="<GOOGLE_ID>")
```

Confirm the returned `account_name` matches the property the user mentioned. If it doesn't match, stop and ask the user.

**Then verify the Meta account is not multi-brand:** run `Supermetrics:campaign_and_resource_get(ds_id="FA", account_id="<META_ID>", resource_type="campaigns")` and scan the campaign names. If any belong to OTHER venue brands (Folie, Attiko, Isola, Moi Spa, Raise, etc.), the account is shared — **every** Meta query below must carry `filters="adcampaign_name =@ METT"`. This is non-negotiable (see Lesson 34). Do the same campaign-list check for Google Ads.

### Step 2 — Pull data (run all queries in parallel, then retrieve)

Default date range: most recent ~58-day window unless user specifies. Always check current date with `Supermetrics:get_today` first to compute a rolling window.

Run all 9 queries in parallel:

| # | Source | Fields | Purpose |
|---|---|---|---|
| 1 | GAWA | `date,sessions,totalUsers,ecommercePurchases,purchaseRevenue` | Daily GA4 revenue/bookings/sessions |
| 2 | FA | `date,cost,impressions,clicks,link_clicks,landing_page_views,offsite_conversions_fb_pixel_purchase,offsite_conversion_value_fb_pixel_purchase` **+ `filters="adcampaign_name =@ METT"`** | Daily Meta spend/conversions — **filter is mandatory; account may be multi-brand (see Lesson 34)** |
| 3 | AW | `Date,Cost,Impressions,Clicks,Conversions,ConversionValue` | Daily Google spend/conversions |
| 4a | GAWA | `totalUsers,sessions,engagedSessions,userEngagementDuration` (1 row, full period) | **Website Traffic Overview totals band on Page I (mandatory)** |
| 4b | GAWA | `sessionDefaultChannelGroup,totalUsers,newUsers,sessions,engagedSessions,bounceRate,userEngagementDuration,screenPageViews` (max 15 rows) | **Website Traffic Overview channel-group table on Page I (mandatory)** |
| 5 | GAWA | `country,city,sessions,totalUsers,userEngagementDuration,bounceRate,engagedSessions,transactions,purchaseRevenue` (max 30 rows) | **Geo Performance table on Page V (mandatory)** — top 12 country/city by bookings (sorted desc) |
| 7 | GAWA | `pagePath,sessions,screenPageViews` (max 25 rows) | Top viewed pages |
| 7b | GAWA | `landingPage,sessions,bounceRate` (max 25 rows) | Top landing pages |
| 8 | AW | `Campaignname,AdvertisingChannelType,Cost,Impressions,Clicks,Conversions,ConversionValue` | Google campaigns |
| 9 | FA | `adcampaign_name,adset_name,cost,impressions,clicks,link_clicks,landing_page_views,ctr,offsite_conversions_fb_pixel_purchase,offsite_conversion_value_fb_pixel_purchase` **+ `filters="adcampaign_name =@ METT"`** | Meta ad sets — pull WITH `adcampaign_name` so you can confirm each ad set is METT (Lesson 34) |

Note: query #6 (deviceCategory split) is no longer used — Page V kept its device chart but Page VI lost "Device split" + "New vs returning" cards in May 2026 cleanup. Skip the pull.

Plus two queries for the Creative tab (Page VII):

| 10 | FA | `date,ad_id,ad_name,cost,impressions,clicks` filter `cost > 1 AND adcampaign_name =@ METT` max_rows=5000 | **Daily per-creative data** for live recompute — filter to METT campaigns only (Lesson 34) |
| 11 | FA | `ad_id,ad_name,creative_object_type,creative_image_url,promoted_post_full_picture,cost` filter `cost > 100 AND adcampaign_name =@ METT` (last 30 days) | Fresh thumbnails per creative format — METT campaigns only (Lesson 34) |

### Step 2b — Refresh creative thumbnails on EVERY build

Meta signed image URLs include an `oe=` (expiry) param. **Critical field choice (see Lesson 39):** always pull **`creative_image_url`** — it returns high-res `cdninstagram.com` `t51` images valid for **weeks** (some reels fall back to a fresh `fbcdn` `t45`, also multi-day). **Never use `creative_thumbnail_url`** — 64px `fbcdn` `p64x64` URLs that expire in ~days and were the root cause of repeated blank/blurry thumbnails. Copying stale URLs from an old reference file makes the cards 404 to the gradient fallback.

**Always re-pull thumbnail URLs from Supermetrics on every build (query #11).**

URL choice depends on `creative_object_type`:
- **`SHARE` (carousel)** → use `creative_image_url`. Returns the **first card image** from Instagram CDN (`scontent-fra*.cdninstagram.com`). Higher resolution, longer-lived signed URLs.
- **`VIDEO` (Reels/Videos)** → use `promoted_post_full_picture`. Returns the **Facebook video poster frame** (`t15.5256-10` URLs). Better than `creative_image_url` for reels (which sometimes returns a generic image).
- **Image ads** → use `creative_image_url`.

**Note:** Cannot combine `carousel_card_image_url` + `video_asset_thumbnail_url` in one query (`IllegalDimensionMetricCombinationException`). Use the field set above — it works for all formats in a single query.

### Step 2c — Build per-creative daily arrays (query #10 → JS)

The Creative tab cards must update when the user picks different date ranges. Hardcoded numbers like `spend: '1,200'` are forbidden — they ignore the filter and look like fake data.

Workflow:

1. Run query #10 to get daily ad-level data (~280-300 rows for a 60-day window).
2. Map each `ad_name` to one of the 8 creative slot indexes (e.g. `'Reel - 27 Mar 2026'` → slot 2 "Opening RTG"). Build a partial-match classifier function in Python.
3. Aggregate to three 8×N JavaScript arrays:
   - `creativeDailySpend[slot][day]` — daily spend per creative slot
   - `creativeDailyImp[slot][day]` — daily impressions
   - `creativeDailyClk[slot][day]` — daily clicks
4. Inject these arrays right after `googleSpendArr` in the data section.
5. Strip `spend`/`imp`/`clicks`/`ctr` from the `creatives = [...]` array — keep only `fmt`, `offer`, `name`, `thumb`, `permalink`. Stats are now computed live.
6. `buildCreatives()` in the reference file already implements:
   - Index lookup from `state.startDate`/`state.endDate`
   - Per-slot sum across the active window
   - CTR = clicks / impressions × 100
   - **Re-rank by spend descending** every render
   - **Hide creatives with zero spend** in the active window

7. Confirm `applyFilters()` resets `renderedPages = {}` and calls `initPage(activeTab)` so the Creative tab rebuilds when filters change. Pre-ship audit Check 7 verifies this wiring.

### Step 3 — Crawl the property's offers page

Use `web_search` to find real offer URLs for the property:

```
web_search("METT <property> offers official site")
```

Use returned URLs that match the pattern `metthotelsandresorts.com/<property>/offers/...` for the offers table on Page III. Avoid invented or aggregator URLs.

### Step 4 — Apply the attribution model

GA4 misclassifies most paid revenue as Referral because the booking engine sits on `reservations.sunsethotelsandresorts.com`. The dashboard re-attributes using these rules **(do not change)**:
- 100% of `metthotelsandresorts.com / referral` → paid
- 55% of Direct → paid
- 75% of Unassigned → paid
- 100% of UTM-tagged paid sessions → paid

Result locked at **82.5% of revenue, 82.3% of bookings** as paid. The remaining ~17% is true direct/organic.

**Google : Meta split** of paid revenue and bookings:
- Marbella: **59 : 41**
- Singapore: **59 : 41** (was 58/42 in earlier builds — corrected to 59/41 to match data)
- For new properties: use the ratio of Google paid sessions to Meta paid sessions from query #4. Round to nearest whole percent.

### Step 5 — Build the dashboard

**CRITICAL ORDER OF OPERATIONS** (this is the #1 source of bugs):
1. Copy the closest reference file (`reference/METT_Marbella_reference.html` for EUR, `reference/METT_Singapore_reference.html` for USD)
2. **Do all property-specific row swaps FIRST** — Google campaigns rows, Meta ad sets rows, offers rows, top page rows, landing page rows, markets rows, creative cards array, recommendations text. Match the existing row patterns by their `name` cell text (e.g. `'PMAX_METT Marbella'`) and replace the entire row.
3. **Then do the currency conversion SECOND** — daily arrays, BASELINE, all `data-base` attributes, JS chart values, KPI defaults.
4. **Then update the date strings** — see "Date label drift" section below for the 6 places these live.
5. **Then refresh creative thumb URLs** with fresh `creative_image_url` values from query #10.

If you do these in the wrong order, the row-swap pattern matches will fail (because `data-base` attribute formats changed during currency conversion), and you'll end up with Marbella content surviving in a non-Marbella build.

### Step 6 — MANDATORY audit before shipping

The skill folder includes `scripts/pre_ship_audit.py` which automates **9 critical checks**. **Always run it before calling `present_files`:**

```bash
python3 /mnt/user-data/outputs/METT-report-SKILL/scripts/pre_ship_audit.py /path/to/METT_<Property>.html
```

The audit verifies:
1. JS syntax via `node --check`
2. No cross-property leaks (Marbella in non-Marbella builds, etc.)
3. No currency leaks (€ in USD builds, $ in EUR builds, S$ anywhere except code)
4. Footer shows correct GA4 / Meta / Google Ads account IDs for THIS property
5. Page I has the Total Paid Spend KPI card
6. Calendar uses the bulletproof click handler with Date midnight normalization
7. `scaleTableCells(rangeMult)` is wired into `updateKPIs` so date filters update tables
8. All offer URLs match the property's path prefix (e.g. `/singapore/offers/...`) — note: the regex must put the leading `/` inside the capture group, otherwise this check false-fails (see Lesson 26)
9. **All visible date labels match the data range** — catches the "showing Apr 26 in header but data goes to Apr 27" drift bug
10. **Per-section `<div>` balance** — for every `<section class="page" ...>...</section>`, count `<div\b` and `</div>` occurrences inside it. They MUST match exactly. A single off-by-one here causes content to leak onto every tab (see Lesson 23). Also verify total `<section>` opens = closes = 7.

If the audit fails, fix the issues and re-run. Do not ship a failing build.

If you don't have access to the script (running inline), do these checks manually:

```bash
# JS syntax
python3 -c "import re; html=open('METT_<P>.html').read(); s=re.findall(r'<script>([\s\S]*?)</script>', html)[0]; open('/tmp/check.js','w').write(s)"
node --check /tmp/check.js

# Property leak audit (for non-Marbella builds)
grep -c "Marbella\|marbella" METT_<Property>.html  # must be 0

# Currency leak audit (for USD builds)
grep -c "&euro;\|€\|S\$" METT_<Property>.html  # must be 0

# Date label audit (the most-missed bug)
grep -n "Apr [0-9]\|Mar [0-9]" METT_<Property>.html | grep -v "Updated"
# All visible "Mar X – Apr Y" labels must match the actual end date in the dates array

# Per-section div balance (catches the "Market efficiency on every tab" regression)
python3 -c "
import re
html = open('METT_<Property>.html').read()
sections = re.findall(r'<section class=\"page[^\"]*\"[^>]*id=\"(page-\w+)\">(.*?)</section>', html, re.DOTALL)
print(f'{len(sections)} sections found (must be 7)')
for sid, body in sections:
    o = len(re.findall(r'<div\b', body)); c = len(re.findall(r'</div>', body))
    print(f'  {sid:25s} open={o} close={c} {\"OK\" if o==c else \"MISMATCH\"}')
"
```

Then ship:

```bash
cp METT_<Property>.html /mnt/user-data/outputs/
```

Then call `present_files` with the output path.

## Architecture (do not modify)

### Data layer
- **Daily arrays** indexed by ISO date: `dates`, `ga4Revenue`, `ga4Bookings`, `ga4Sessions`, `metaSpendArr`, `googleSpendArr`
- **`dateIndex`** map for O(1) date→index lookup
- **`getScaledData()`** returns sliced data for the active date range plus computed totals and `rangeMult` (selected-period revenue ÷ full-period revenue, used to scale proportional metrics)
- **`BASELINE`** constants hold full-period totals

### Filter UX
- Single date-range button → calendar popover with 2 months side-by-side
- Sidebar presets: All data, Yesterday, Last 7/14/30/90 days, This/Last week, **This month (default active — anchored to the latest day in `dates[]`, see Lesson 35)**, Last month. **NO "Year to date"** — removed across all properties (doesn't make sense when data only spans 2-3 months). The report opens on the **latest month**, not the full window; "All data" stays one click away.
- Two-click range selection with hover preview (rose-tinted in-range cells)
- Auto-swap if user clicks earlier date second
- **Calendar bounds are clamped to the data range** (`_dataStart` and `_dataEnd` derived from the `dates[]` array). Days outside the range render as muted/disabled, and prev/next chevrons auto-disable when no data exists in that direction. See "Calendar bounds clamping" below.

### Calendar bounds clamping (do not omit)

The calendar must visually + behaviorally enforce the data range — users cannot pick dates that don't exist. Three places need the bounds check:

**1. Inside `renderMonthGrid()`, before rendering each day cell:**
```javascript
for (var day = 1; day <= lastDay.getDate(); day++) {
  var cellDate = new Date(monthDate.getFullYear(), monthDate.getMonth(), day);
  var outOfBounds = (cellDate < _dataStart) || (cellDate > _dataEnd);
  if (outOfBounds) {
    html += '<button class="cal-day muted" disabled>' + day + '</button>';
    continue;
  }
  // ... rest of cell rendering
}
```

**2. Inside `renderCalendar()`, disable prev/next chevrons at edges:**
```javascript
var prevBtn = document.getElementById('cal-prev');
var nextBtn = document.getElementById('cal-next');
if (prevBtn) {
  var prevMonthEnd = new Date(startM.getFullYear(), startM.getMonth(), 0);
  var noPrevData = (prevMonthEnd < _dataStart);
  prevBtn.disabled = noPrevData;
  prevBtn.style.opacity = noPrevData ? '0.3' : '1';
  prevBtn.style.cursor = noPrevData ? 'not-allowed' : 'pointer';
}
if (nextBtn) {
  var nextMonthStart = new Date(endM.getFullYear(), endM.getMonth() + 1, 1);
  var noNextData = (nextMonthStart > _dataEnd);
  nextBtn.disabled = noNextData;
  nextBtn.style.opacity = noNextData ? '0.3' : '1';
  nextBtn.style.cursor = noNextData ? 'not-allowed' : 'pointer';
}
```

**3. Inside the prev/next click handlers, defensive re-check:**
```javascript
document.getElementById('cal-prev').addEventListener('click', function() {
  if (this.disabled) return;
  var candidate = new Date(state.viewMonth.getFullYear(), state.viewMonth.getMonth() - 1, 1);
  var candidateLastDay = new Date(candidate.getFullYear(), candidate.getMonth() + 1, 0);
  if (candidateLastDay < _dataStart) return;
  state.viewMonth = candidate;
  renderCalendar();
});
```

**Inside `applyPreset()`, clamp the resulting range to data bounds:**
```javascript
if (s < dataStart) s = dataStart;
if (e > dataEnd)   e = dataEnd;
if (s > dataEnd)   s = dataEnd;
```

This is defense in depth — three layers ensure no out-of-range date can ever be selected, regardless of preset choice or manual navigation.

### Calendar click handler — BULLETPROOF VERSION (do not deviate)

The calendar click handler MUST normalize all Date objects to midnight before comparison. The reference files contain the bulletproof version. If you ever rebuild this from scratch:

```javascript
// In openPicker — clone and normalize to midnight
state.tempStart = state.startDate ? new Date(state.startDate.getFullYear(), state.startDate.getMonth(), state.startDate.getDate()) : null;
state.tempEnd = state.endDate ? new Date(state.endDate.getFullYear(), state.endDate.getMonth(), state.endDate.getDate()) : null;

// In click handler — preventDefault, stopPropagation, re-normalize defensively
btns[k].addEventListener('click', function(evt) {
  evt.preventDefault();
  evt.stopPropagation();
  var ts = parseInt(evt.currentTarget.getAttribute('data-ts'), 10);
  var picked = new Date(ts);
  picked = new Date(picked.getFullYear(), picked.getMonth(), picked.getDate());

  // Re-normalize tempStart and tempEnd to midnight before comparison
  if (state.tempStart && !(state.tempStart instanceof Date)) state.tempStart = new Date(state.tempStart);
  if (state.tempStart) state.tempStart = new Date(state.tempStart.getFullYear(), state.tempStart.getMonth(), state.tempStart.getDate());
  if (state.tempEnd && !(state.tempEnd instanceof Date)) state.tempEnd = new Date(state.tempEnd);
  if (state.tempEnd) state.tempEnd = new Date(state.tempEnd.getFullYear(), state.tempEnd.getMonth(), state.tempEnd.getDate());

  if (!state.tempStart || (state.tempStart && state.tempEnd)) {
    // Fresh selection
    state.tempStart = picked;
    state.tempEnd = null;
  } else {
    var pickedTime = picked.getTime();
    var startTime = state.tempStart.getTime();
    if (pickedTime === startTime) state.tempEnd = picked;
    else if (pickedTime < startTime) { state.tempEnd = state.tempStart; state.tempStart = picked; }
    else state.tempEnd = picked;
  }
  state.activePreset = null;
  clearHoverPreview();
  renderPresetActive();
  renderCalendar();
});
```

Without midnight normalization, comparisons between same-day Dates with different time-of-day values silently fail.

### Chart safety
`SafeChart` wrapper destroys `Chart.getChart(canvas)` before creating new. `destroyAllCharts()` called in `applyFilters()` before re-render. Lazy rendering: `renderedPages` cache — only the active tab rebuilds immediately.

### What gets updated on filter apply
1. `updateKPIs()` — all KPI cards across Pages I/II/IV
2. `scaleTableCells(rangeMult)` — every `<td data-base="..." data-fmt="eur|pct|int">` cell rewrites its text scaled by `rangeMult`
3. Chart builders for the active tab use `getScaledData()` and `rangeMult` to recompute charts

⚠️ **These must ALSO run once on INITIAL LOAD**, from `init()`, after the default range is committed into `state` — not only on Apply. If `init()` only calls `initPage('overview')`, the KPI cards keep their static HTML values and silently show the wrong period whenever the default isn't the full window. This is the single most dangerous render bug in the build — see Lessons 35–38.

## Visual design (locked)

### Brand palette
```
--bg: #FFFFFF; --surface: #FFFFFF; --surface-2: #F7F5F2;
--ink: #0E2340 (navy); --ink-2: #2D3E56; --ink-3: #6B7280; --ink-4: #B0B7C1;
--line: #E5E7EB; --line-2: #D1D5DB;
--gold: #C89B94 (dusty rose); --gold-2: #A67D76; --gold-soft: #F5E6E2; --sand: #E8D4CF;
--navy: #0E2340; --navy-2: #1A3558;
--success: #4F7A5A; --warn: #B07A3F; --danger: #9E4B4B;
--font: 'Calibri', sans-serif
```

### Typography & tone
- Font: **Calibri** (user requirement — do not change)
- Tone: luxury hospitality, executive-level
- White background, navy primary, dusty-rose accents
- **No emojis**

### Tab structure (7 tabs)
1. **Overview** — just "Overview", not "Executive Overview". **9 KPI cards in 3×3 grid**, including **Total Paid Spend** AND **Website Conversion Rate** (REQUIRED, do not omit either). NO verbose subtitle paragraph — just the eyebrow ("Page I") and the heading.
2. Paid Media
3. Offers & Activations
4. Attribution
5. Booking Funnel
6. Markets & Audience
7. Creative

**Tab VIII (Recommendations) has been removed across all properties.** Do not add it back. If a legacy reference HTML still has it, delete: (a) the `<button class="tab" data-tab="action">` from the nav, (b) the entire `<section class="page" id="page-action">` block, and (c) any `action:` entry in the `pageBuilders` registry.

### Page heading rule (apply to ALL pages)
Every page-head shows ONLY the eyebrow (e.g. "Page I") and the `<h2>` title. **No `<p class="sub">` subtitle paragraphs explaining what the page is.** The data tells the story; we don't narrate it. This applies to Pages I through VII.

### Insight boxes (the pink `<div class="insight">` blocks)
Pages I, II, IV are allowed to keep their insight boxes (those carry the corrected-attribution narrative that justifies the dashboard's headline number). Pages III, V, VI, VII do NOT get insight boxes — they were removed because the data already speaks for itself. When building a new property, only insert insight boxes on Pages I, II, IV.

### Page I KPI grid (9 cards in 3×3 layout, in this exact order)

Use CSS class `kpi-grid cols-9` (3 columns × 3 rows). Add this CSS rule alongside the existing cols-8: `.kpi-grid.cols-9 { grid-template-columns: repeat(3, 1fr); }` plus matching responsive breakpoints (2 cols at tablet, 1 col at mobile).

The narrative reads: revenue → bookings → paid revenue → paid bookings → **spend** → ROAS → CPB → AOV → **Website CVR**.

| Row 1 | Row 2 | Row 3 |
|---|---|---|
| Total Revenue (hero) | Total Bookings | Paid Media Revenue (hero) |
| Paid Bookings | Total Paid Spend | Blended ROAS (hero) |
| Cost per Booking | Avg Booking Value | **Website Conversion Rate** |

**Card details:**
- Total Revenue → main value + subtitle "X days · Y bookings" (Y must match the actual `BASELINE.totalBookings` — watch for drift)
- Total Paid Spend → subtitle "Meta €X · Google €Y"
- **Website Conversion Rate** → `bookings / sessions × 100`, displayed as `0.67%` with subtitle `"318 bookings / 47,374 sessions"` (numerator/denominator visible so the client can see the math). The unit `%` goes in a `<span class="unit">` for proper sizing.

```html
<div class="kpi" id="kpi-cvr">
  <div class="label">Website conversion rate</div>
  <div class="value">{rate}<span class="unit">%</span></div>
  <div class="delta">{bookings} bookings / {sessions} sessions</div>
</div>
```

Do NOT confuse this with **paid CVR** (paid_bookings / paid_sessions). The Page I card is **website-wide** — the bottom-of-funnel efficiency metric the client tracks alongside revenue and ROAS. Luxury hospitality benchmark: 0.5-1.0% is strong (lower than budget hotels because of longer consideration cycles + high AOV).

Do NOT include a separate generic "Conversion Rate" card — earlier versions had it removed for being ambiguous at exec level; the labeled "Website conversion rate" is the answer.

### Layout parity — the drift guard (MANDATORY)

**Root cause of all Page I drift:** structure was treated as a per-build decision. It is not. The Page I card set above is **canonical and identical for every property** — only the *values* change (data + currency), never the card IDs, labels, order, or fixed subtitle copy. The skeleton (`METT_Skeleton.html`) is the structural source of truth and MUST already match this spec; if you ever edit the layout, edit the skeleton and this section together, never a single property in isolation.

**Canonical card fingerprint (id · label · fixed subtitle):**
1. `kpi-total-rev` · Total revenue · *(dynamic: "N days · M bookings")*
2. `kpi-total-bkg` · Total bookings · "GA4 ecommerce purchases"
3. `kpi-paid-rev` · Paid media revenue · "Driving 82.5% of revenue"
4. `kpi-paid-bkg` · Paid bookings · "82.3% of all bookings"
5. `kpi-total-spend` · Total paid spend · *(dynamic: "Meta {cur}X · Google {cur}Y")*
6. `kpi-roas` · Blended ROAS · "Growth-phase return"
7. `kpi-cpb` · Cost per booking · "Paid spend / paid bookings"
8. `kpi-aov` · Avg booking value · "Luxury market positioning"
9. `kpi-cvr` · Website conversion rate · *(dynamic: "M bookings / S sessions")*

> Note: subtitle #6 "Growth-phase return" is editorial and reads oddly on mature properties (e.g. Marbella 36.6×). It is uniform by default; if a property's ROAS is clearly mature, that single line may be tuned — nothing else in the fingerprint may change.

**Gate:** run `scripts/mett_layout_audit.py` against every finished property BEFORE `present_files`. It checks card IDs + labels (strict) and fixed subtitle copy, ignoring per-property numbers. Exit 0 = ship; exit 1 = drift, fix before shipping.

```bash
python3 /mnt/user-data/outputs/METT-report-SKILL/scripts/mett_layout_audit.py /path/to/METT_<Property>.html
```

This is what would have caught Marbella's old card set (Website sessions / Blended CTR / Engagement rate) before it ever reached the client.

### Page I mandatory layout (in this exact order)

After the KPI grid, Page I has THREE sections:

1. **Bookings trend + Revenue by channel** (2-column `grid-2` card row)
2. **Corrected attribution insight box** (the pink `<div class="insight">` that explains the 82.5% / 82.3% paid-influenced model)
3. **Website Traffic Overview** (full-width card with 4-cell totals band + 10-column channel-group table) — see below

### Website Traffic Overview (Page I, mandatory · May 2026 spec)

Replaces the older "Traffic by source & medium" 6-column table. Sits at the bottom of Page I, full-width. Two parts: a totals band on top, a channel-group breakdown table below.

**Part A — Totals band (4 cells):**
- Users
- Sessions
- Engaged sessions
- Avg time/session (computed as `userEngagementDuration / sessions`, formatted `Xm YYs` or `Ns`)

Numbers carry `data-base` / `data-fmt` for date-filter scaling. Avg time/session is a ratio metric, so display the full-period value without scaling (or compute on the fly from scaled engagement + sessions).

**Part B — Channel-group breakdown (10 columns):**
- Default channel group
- Users
- New users
- Sessions
- Engaged sessions
- Engagement rate
- Avg time/session (`Xm YYs` or `Ns`)
- Sessions/user (1 decimal)
- Bounce rate (pill: 🟢 <25%, 🟡 25-40%, 🔴 >40%)
- Views/session (`screenPageViews / sessions`, 2 decimals)

Ranked by sessions descending.

**Data pull:**
```
# For the totals band
GAWA fields: totalUsers, sessions, engagedSessions, userEngagementDuration
(returns 1 row of full-period totals)

# For the breakdown
GAWA fields: sessionDefaultChannelGroup, totalUsers, newUsers, sessions,
             engagedSessions, bounceRate, userEngagementDuration, screenPageViews
Max rows: 15 (typically 8-12 actual channel groups)
```

**HTML template:**
```html
<div class="card" style="margin-top: 18px;">
  <div class="card-head"><div><h3>Website traffic overview</h3>
    <div class="card-sub">Site-wide totals &middot; full period &middot; channel-group breakdown ranked by sessions</div></div></div>

  <div class="traffic-totals" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;padding:14px 16px;background:var(--surface-2);border:1px solid var(--line);border-radius:6px;">
    <div><div style="font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--ink-3);margin-bottom:4px;">Users</div><div style="font-size:22px;font-weight:700;color:var(--ink);" data-base="NNN" data-fmt="int">NN,NNN</div></div>
    <!-- repeat for Sessions, Engaged sessions, Avg time/session -->
  </div>

  <div class="table-wrap">
    <table class="data">
      <thead><tr>
        <th>Default channel group</th>
        <th class="num">Users</th><th class="num">New users</th>
        <th class="num">Sessions</th><th class="num">Engaged sessions</th>
        <th class="num">Engagement rate</th><th class="num">Avg time/session</th>
        <th class="num">Sessions/user</th><th class="num">Bounce rate</th>
        <th class="num">Views/session</th>
      </tr></thead>
      <tbody><!-- rows ranked by sessions desc --></tbody>
    </table>
  </div>
</div>
```

**Note:** the older "Traffic by source & medium" 6-column table is deprecated. Older reference HTMLs may still have it — strip and replace.

### Geo Performance table (Page V, mandatory)

Located on Page V at the bottom of the section. Top 12 country/city combinations, **sorted by bookings descending** (the commercial-priority order, not by sessions).

**Columns (in this order, 10 total):**
Country · City · Users · Sessions · Engagement · **Avg time/session** · **Bounce rate** · Bookings · Revenue · CVR

Avg time/session and bounce rate are computed the same way as the Traffic table — `userEngagementDuration / sessions` for time, native `bounceRate` from GA4 for bounce. Same pill color rules (🟢 <25%, 🟡 25-40%, 🔴 >40%). CVR pill: 🟢 ≥1.5%, 🟡 0.5-1.5%, 🔴 <0.5%.

### Market Efficiency table (Page VI, May 2026 update)

Add the same **totals-band pattern** as Website Traffic Overview above the existing market table. 4 cells: Sessions · Paid spend · Revenue · Bookings — aggregated across all 10 market rows. Wrap monetary values with a smaller `$` span (see Lesson 28 in "Common errors & fixes"). Removes the need for the reader to mentally sum the table.

Also: ensure "Top markets by revenue" and "Top markets by bookings" cards above Market Efficiency are wrapped in `<div class="grid-2">...</div>` — this is a regression spot (see Lesson 23). And delete the "Device split" / "New vs returning users" `<div class="grid-2">` row that used to sit at the bottom of Page VI — both canvases were empty placeholders.

### Page V layout (cleaned)

Page V contains, in order:
1. **Page head**: eyebrow ("Page V") + `<h2>Booking funnel & website</h2>`. NO subtitle paragraph.
2. **Funnel + Device** (2-column row)
3. **Top viewed pages + Top landing pages** (2-column row). 3 columns each. NO captions below either table. NO insight box between them.
4. **Geo performance** (full-width, 10 columns with avg time/session + bounce rate)

Do NOT add: "End-to-end funnel from first session..." subtitle, "Two issues to fix..." caption, or the "biggest funnel issue here is cross-domain attribution loss" insight box. All were removed in the May 2026 cleanup.

### Creative cards (Page VII) — square, 4 per row, overlay style

Locked layout:
- **Desktop**: 4 columns, `grid-template-columns: repeat(4, 1fr); gap: 14px;`
- **Tablet (~768-1024px)**: 3 columns
- **Mobile (<768px)**: 2 columns
- Each card is `aspect-ratio: 1 / 1` (true square)
- Image fills the entire square (full-bleed `object-fit: cover`)
- Navy gradient overlay fades from transparent at top → 95% opaque navy at bottom
- All text (offer name, ad set name, Spend/Impr/CTR stats) sits on the bottom 40% of the image, white with subtle text shadow
- Card is a single `<a>` tag with `display: block; text-decoration: none;` (CRITICAL — without `display: block`, `aspect-ratio` is silently ignored on inline `<a>` elements)
- The `buildCreatives()` function uses the **DOM API** (`createElement`/`appendChild`), NOT innerHTML string concatenation — innerHTML quote escaping inside `onerror` attributes was a real bug that broke the layout
- Fallback SVG is **base64-encoded** (`btoa(unescape(encodeURIComponent(svgMarkup)))`) — URL-encoded SVGs in `data:` URIs hit quote-collision bugs

## Property-specific data slots

For each property, prepare these data points:

```python
PROPERTY = {
    "name": "METT <Property>",
    "currency": "EUR" or "USD",
    "currency_symbol": "&euro;" or "$",
    "ga4_id": "...",
    "meta_id": "act_...",
    "google_id": "...",  # no dashes
    "google_id_display": "...-...-....",  # with dashes for footer
    "offer_urls": [
        # Real /<slug>/offers/... URLs from web_search
    ],
    "page_paths": [
        # Real GA4 page paths from query #7
    ],
    "google_meta_split": (0.59, 0.41),  # locked at 59/41 for both Marbella and Singapore
    "fx_rate_to_dashboard_currency": 1.0,  # or e.g. 0.784 for SGD→USD
    "fx_rate_source": "wise.com (verified <date>)",
}
```

### Verified account IDs (confirmed against live Supermetrics — copy verbatim)

| Property | GA4 | Meta | Google (plain / footer) | Native currency → dashboard |
|---|---|---|---|---|
| Marbella | `327114117` | `act_1205759304496215` | `8964815527` / `896-481-5527` | EUR → EUR |
| Singapore | `496938229` | `act_2240093806419894` | `8360908539` / `836-090-8539` | mixed (GA4 SGD, ads USD) → USD |
| Bodrum | `307945131` | `act_797332184222785` | `2898288837` / `289-828-8837` | TRY (all 3) → EUR |

`ds_id` values: GA4 = `GAWA`, Meta = `FA`, Google = `AW`.

## Date label drift — the most-missed bug

When extending data to a new day, you MUST update the date string in **6 places**, not just the data arrays:

1. `var dates = [...]` array (the source of truth)
2. The `endDate: new Date(2026, 3, NN)` in the state object — **if you forget this, the dashboard's default view clips the last day off the displayed totals**
3. The "LIVE · MAR 1 – APR NN, 2026" pill at the top of the page
4. The date range button label (`<span class="date-value">1 Mar – NN Apr 2026</span>`)
5. The "Showing all data · 1 Mar – NN Apr 2026" filter indicator strip
6. The "All data" calendar preset's right-aligned subtitle (`Mar 1 – Apr NN`)
7. The two JS comment headers documenting the data range
8. The "Updated NN Apr 2026 · HH:MM UTC" timestamp (separate concept — represents the build time, not the data range, but should still be current)

The `pre_ship_audit.py` script has Check 9 specifically to catch any visible date label that doesn't match the data array length. **It excludes "Updated NN Apr" timestamps** because those are runtime-refresh dates, not data-range dates.

## Common errors & fixes

**1. "Marbella" leaks into a non-Marbella build.**
Always run `grep -i "marbella\|<other_property>"` after the build. If the property is not Marbella, the result must be 0. The most common cause: row-level swaps in tables (Google campaigns, offers, landing pages) where the `data-base` conversion ran *before* the row swap, breaking the pattern match. **Fix order: do all row swaps FIRST, currency conversion SECOND.**

Locations where Marbella content most often survives:
- Google campaigns table on Page II (`PMAX_METT Marbella`, `SEM_METT Marbella`, `SEM · Azure Marbella`)
- Offers table on Page III (`/marbella/offers/...` URLs and offer names)
- Top landing pages on Page V (`/marbella/`, `/marbella/booking/`, etc.)
- Page III KPI banner ("Best offer: Early Booking €58,940")
- Page IV conversion path widget (5 path values)
- Page VII top revenue creative card ("Plan Ahead €10,670")
- Page VIII recommendation text (Marbella PMAX numbers, market line, malformed-URL bullet, post-boost bullet)
- Insight text on Page V ("The same cross-domain attribution loss seen on Marbella")

Audit by `grep` and fix every single one before shipping.

**2. JS syntax errors after edits.**
Always run `node --check` on the extracted script. Common breakages: unbalanced quotes in template literals, trailing commas in object literals on older Node.

**3. Charts not updating when filter changes.**
The chart builder must use `getScaledData()` not `BASELINE`. Hardcoded numbers in chart `data:` arrays must be wrapped in `sm(N)` (where `sm = v => Math.round(v * rangeMult)`).

**4. Currency symbol leaks (e.g. € shown on a USD dashboard).**
After currency swap, run `grep -c "&euro;\|€"` (or whichever symbols don't belong). Should be 0. Locations to check:
- Meta ad sets table CPC column (`&euro;0.08`, `&euro;0.17`)
- Page III KPI banner (`<span class="cur">&euro;</span>172,847`)
- Page IV conversion path values (`<div class="path-val">&euro;79,740</div>`)
- Page VII top revenue creative delta
- Page VIII recommendation bullets
- `fmtEur()` and `fmtK()` JS functions
- Every `setKpi('kpi-XXX', '<span class="cur">\u20AC</span>...')` call

**5. Static numbers showing across date filter.**
Cell needs `data-base="N" data-fmt="eur|pct|int"` and `scaleTableCells(rangeMult)` must be called from `updateKPIs()`.

**6. Calendar can't pick dates / second click resets first click.**
Use the bulletproof click handler from the "Calendar click handler" section above. The bug is caused by Date objects with non-midnight time-of-day values causing `picked < tempStart` comparisons to behave unexpectedly. The fix: normalize every Date to `new Date(y, m, d)` before any comparison.

**7. Page II/III/IV/V/VI tabs don't update when date filter changes.**
Each affected page needs:
- KPI cards with explicit `id="kpi-XXX"` attributes
- Numeric table cells with `data-base="N"` and `data-fmt="eur|int|pct"` attributes
- Chart hardcoded values wrapped in `sm(N)` so they scale with `rangeMult`
- A call to `setKpi(...)`, `setText(...)`, or `scaleTableCells(rangeMult)` inside `updateKPIs()`

**8. SGD→USD conversion incomplete.**
The Singapore conversion has many touchpoints. After conversion, audit:
- `grep -c 'S\$\|SGD'` should be 0 (no SGD references)
- `grep -c '&euro;\|€'` should be 0 (no euro references)
- Check the Meta ad sets table — those rows often retain old SGD CPC values like `S$0.40`
- Check creative cards — revenue/spend strings need conversion (×0.784)
- Check recommendation text — bullets reference specific dollar amounts

**9. Creative cards show 8 identical fallback SVGs (the "repetitive man" bug).**
Facebook signed thumbnail URLs expire every ~24 hours. If you copy thumb URLs from a 1-day-old reference file, they'll all 404 and fall back to the navy SVG default. **Solution: always re-pull `creative_image_url` from Supermetrics on every build (query #10).** These come from Instagram's CDN and are higher quality and fresher than FB scontent thumbnails.

**10. Creative cards rendering with no images / collapsed / broken.**
Two real bugs we hit:
- The `.creative` element is an `<a>` tag — `aspect-ratio: 1/1` is **silently ignored on inline elements**. Must add `display: block; text-decoration: none;` to the CSS.
- The `onerror` attribute with a URL-encoded SVG fallback hits quote-collision bugs when special characters end up inside `onerror="this.src='...'"`. **Solution**: use the DOM API (`createElement`, `appendChild`) instead of innerHTML string building, and base64-encode the fallback SVG.

**11. Date label drift — UI shows old end date even though data has new days.**
See "Date label drift" section above. Pre-ship audit Check 9 catches this automatically.

**12. Singapore footer shows Marbella account IDs.**
The original swap script matched `GA4 (property 327114117)` but actual footer says `GA4 (327114117)` without the word "property". Audit Check 4 catches this — verifies the correct GA4/Meta/Google account IDs appear in the dashboard for THIS property.

**13. Calendar presets (Last 7/14/30 days) compute wrong date ranges.**
The `applyPreset()` function originally hardcoded `var today = new Date(2026, 3, 23)` (the data end-date when first written). When data was extended to Apr 27, 30, etc., the presets kept computing relative to Apr 23. Result: "Last 7 days" showed Apr 17 → Apr 23 instead of Apr 24 → Apr 30. **Fix: derive `today` dynamically from the last entry of the `dates[]` array.** Same issue in `state.endDate` initializer. Both must read from `dates[dates.length - 1]` at runtime, never hardcoded. The reference Marbella file already has this — never replace with hardcoded dates.

```javascript
// In applyPreset — derive bounds dynamically from dates[] every time
var firstStr = dates[0].split('-');
var lastStr  = dates[dates.length - 1].split('-');
var dataStart = new Date(parseInt(firstStr[0], 10), parseInt(firstStr[1], 10) - 1, parseInt(firstStr[2], 10));
var dataEnd   = new Date(parseInt(lastStr[0],  10), parseInt(lastStr[1],  10) - 1, parseInt(lastStr[2],  10));
var today = dataEnd;  // Always fresh — never hardcoded
// ... compute s, e per preset
// CLAMP to data bounds so presets like "Last 90 days" work even when data is shorter
if (s < dataStart) s = dataStart;
if (e > dataEnd)   e = dataEnd;
if (s > dataEnd)   s = dataEnd;
```

```javascript
// State initializer — also derive from dates[]
function _parseISO(s) { var p = s.split('-'); return new Date(parseInt(p[0],10), parseInt(p[1],10)-1, parseInt(p[2],10)); }
var _dataStart = _parseISO(dates[0]);
var _dataEnd   = _parseISO(dates[dates.length - 1]);
var state = {
  startDate: _dataStart,
  endDate:   _dataEnd,
  // ...
};
```

**14. Creative cards (Page VII) don't update when date filter changes.**
The original cards had hardcoded `spend: '1,200'`, `imp: '893,625'`, `ctr: '1.10%'` strings that ignored the date filter. **Fix: store per-creative daily arrays + recompute live.** Architecture:

1. Pull daily ad-level data from Supermetrics: `date,ad_id,ad_name,cost,impressions,clicks` filtered to `cost > 1`. Returns ~280-300 rows for a 60-day window.
2. Classify ad names → 8 creative slot indexes (e.g. all "One More Night" ads → slot 0). Build a classifier function — partial-match by name.
3. Build three 8×N arrays: `creativeDailySpend[slot][day]`, `creativeDailyImp`, `creativeDailyClk`. Inject right after `googleSpendArr`.
4. Strip `spend`/`imp`/`clicks`/`ctr` from the `creatives` array — keep only `fmt`, `offer`, `name`, `thumb`, `permalink`.
5. Rewire `buildCreatives()` to:
   - Find `sIdx`/`eIdx` from `state.startDate`/`state.endDate`
   - Sum spend/imp/clk per creative across `[sIdx..eIdx]`
   - Compute CTR = clicks / impressions × 100
   - **Re-rank by spend descending** so #1 is always the top performer in the picked window
   - **Hide creatives with zero spend** in the active window (don't show empty cards)
6. Ensure `applyFilters()` resets `renderedPages = {}` and calls `initPage(activeTab)` so the Creative tab rebuilds.

The reference Marbella file has this fully wired. Verify by picking "Last 7 days" — the card count should drop (creatives that didn't run that week disappear) and the order should re-rank.

**15. NEVER fake creative thumbnails. Always use real ad images.**
The Meta signed CDN URLs expire (weeks for `creative_image_url`; ~days for `creative_thumbnail_url` — see Lesson 39), which matters for a static HTML file. **Do NOT generate branded SVG placeholders to "solve" this — the user has been clear this is wrong.** It misrepresents what's actually running in the ads.

The right approach for thumbnails:
- **Carousels (`creative_object_type: SHARE`)**: use `creative_image_url` — Instagram CDN, returns the first card image (`scontent-fra*.cdninstagram.com`). Higher resolution, longer-lived signed URLs (`oe=` param).
- **Reels/Videos (`creative_object_type: VIDEO`)**: use `promoted_post_full_picture` — Facebook video poster frame (`t15.5256-10` URLs). Better than `creative_image_url` for reels (which sometimes returns a generic image).
- **Image ads**: use `creative_image_url`.

Pull these on every build via Supermetrics:
```
fields: ad_id, ad_name, creative_object_type, creative_image_url, promoted_post_full_picture, cost
filters: cost > 100
date_range: most recent 30 days (gets active ads only)
```

Cannot combine `carousel_card_image_url` + `video_asset_thumbnail_url` in one query (`IllegalDimensionMetricCombinationException` from the API). Use the field combination above instead — it works.

**16. Cannot base64-embed FB CDN images directly.**
Tried downloading `cdninstagram.com` and `fbcdn.net` URLs server-side to embed as `data:image/jpeg;base64,...` for permanence. **The egress proxy returns 403 Forbidden** — Facebook's CDN doesn't allow non-browser User-Agent downloads, and these domains aren't on the allowlist. So the only durable solution for static HTML is the GitHub Actions auto-refresh: pull fresh `creative_image_url` every 6 hours, commit the updated HTML, and the live URL stays fresh forever.

Until that's deployed, static files ship with signed URLs that eventually lapse — but `creative_image_url` buys **weeks**, not ~24h, so a same-day re-pull at handoff is plenty. Document the expiry to the client for one-off files.

**39. Thumbnails: `creative_image_url` only — never `creative_thumbnail_url`. (Definitive; supersedes any ~24h framing above.)**
The blank-thumbnail problem that recurred across sessions traced to one root cause: pulling `creative_thumbnail_url` (64px `fbcdn` `p64x64`, ~days expiry, also blurry). The live/working dashboards (Bodrum, Marbella) all use **`creative_image_url`**, which returns high-res `scontent-*.cdninstagram.com` `t51.71878-15` images with **weeks-long** signed validity (some reels fall back to a fresh `fbcdn` `t45`, still multi-day). One query covers all formats:
```
fields:  ad_id, creative_image_url, ad_name
filters: adcampaign_name =@ METT
date_range: wide enough to include every dashboard creative — older evergreen ads (brand-launch / page-growth reels) drop out if you start too late; use start ~Jan of the current year, max_rows 200
```
Workflow:
- Map each dashboard creative to its image **by `ad_id`** (several ad_ids can legitimately share one image — that's fine).
- Wire **direct from Meta's CDN**: `img.referrerPolicy = 'no-referrer'` then `img.src = c.image`. **No proxy.** The `images.weserv.nl` experiment was a dead end — it can't fetch an already-expired origin, and the requirement is direct-from-CDN.
- **Pre-ship gate:** decode every image's `oe` (`int(oe,16)` → unix seconds) and confirm it is in the **future**; if any is past, re-pull before shipping.
- Supermetrics caches these signed URLs at the account level and will keep returning the same (possibly expired) links on demand — re-auth / query-variation does **not** force a re-mint. The saving grace is that `creative_image_url`'s weeks-long validity means this rarely bites; if it ever does, wait for the cache to roll (a day or two) or hand off within the validity window.

**17. Calendar lets users pick dates outside the data range.**
Without bounds clamping, users can navigate to February or June (when data is Mar–May) and pick days that don't exist. **Fix: implement the three-layer bounds clamping documented in the "Calendar bounds clamping" section above.** Days outside `_dataStart`..`_dataEnd` render as muted/disabled, prev/next chevrons auto-disable at edges, and `applyPreset()` clamps its output.

**18. Year-to-date (YTD) preset is meaningless for short data periods.**
When the data only goes back 2-3 months, "YTD" is identical to "All data" — confusing the client. **Removed from all properties.** When building a new property, do not add a YTD preset button to the calendar sidebar, and do not include the `case 'ytd':` block in `applyPreset()`. The 10 surviving presets are: All data, Yesterday, Last 7/14/30/90 days, This/Last week, This/Last month.

**19. Tab VIII (Recommendations) was removed across all properties.**
Clients found it preachy and ignored it. Three places to clean when removing:
1. The `<button class="tab" data-tab="action">` in the nav
2. The entire `<section class="page" id="page-action">` block
3. The `action: function(){}` (or `action: buildAction`) entry in the `pageBuilders` registry

After removal, JS syntax must still validate. Top nav is now 7 tabs: I Overview · II Paid · III Offers · IV Attribution · V Booking · VI Markets · VII Creative.

**20. Verbose page subtitles and inline captions feel cluttered.**
"Executive overview" → just "Overview". No `<p class="sub">Commercial performance across paid, organic, and direct channels...</p>` paragraphs under page headings. No `<em>Per-page booking revenue is not visible...</em>` captions under tables. No `<div class="insight">` boxes on Pages III, V, VI, VII. The data narrates itself. **Only Pages I, II, IV keep insight boxes** — those carry the corrected-attribution story that justifies the headline numbers.

**21. The "Updated DD MMM YYYY" timestamp drifts.**
The header pill `<div class="timestamp">Updated DD MMM YYYY · HH:MM UTC</div>` is hardcoded. Every time data is extended, this must be manually bumped to match today's date. The pre-ship audit deliberately excludes this from the date-label-drift check (otherwise it would always fail), so the human must remember. When GitHub Actions auto-refresh is in place, replace with a build-time injection: `Updated {{ now() }} UTC`.

**22. Audit script only handled April-format date labels.**
The original `pre_ship_audit.py` Check 9 used regex `(\d{1,2}) Apr 2026` — broke as soon as data extended into May. **The fixed version handles all 12 month abbreviations** and derives the expected end label dynamically from `dates[dates.length - 1]`. Also strips `Updated DD MMM YYYY` timestamps (those are refresh dates, not range labels) and `name: '...'` strings (creative card metadata legitimately references ad launch dates like "10 Apr 2026"). The fix is in the shipped audit script in this skill folder.

**23. Unbalanced `<div>` tags inside a `<section class="page">` cause content to leak onto every tab.**
This was the worst regression in May 2026: a stray `</div>` inside `page-markets` closed the section prematurely, so the Market efficiency card and everything below it became a sibling of the section rather than a child. The tab system uses CSS `.page { display: none; }` / `.page.active { display: block; }` — anything that escapes a `<section class="page">` shows on every tab. Symptom: "Market efficiency appears under every tab", "Creative tab loads weird" (because the Creative section's own DOM is also fighting the orphaned content above it). **Add a per-section div-balance audit** (Check 10 below) to the pre-ship script. Page III had a separate but related bug: `<div class="page-head">` was opened but never closed, so its closing was eaten by the section's `</section>` — same pattern, different page.

**24. Singapore: Google Ads and Meta Ads bill in USD natively. Only GA4 purchaseRevenue is in SGD.**
Earlier sessions assumed Google Ads Singapore returned cost in SGD requiring × 0.7845 conversion. **This is wrong.** Verified by comparing live Supermetrics totals against existing array sums to the cent: Meta `act_2240093806419894` and Google `8360908539` both return cost in USD. The SGD→USD conversion only applies to GA4 `purchaseRevenue` (verified Mar 4: GA4 raw = 3360 SGD → 3360 × 0.7845 = 2,636 USD, matches array value 2635.92). When extending Singapore data: pass spend arrays through directly, multiply GA4 revenue by 0.7845. Document the per-source currency in build-script comments to prevent the next session's drift.

**25. Meta cost filter — use raw `>`, never the HTML entity.**
`Supermetrics:data_query` with `filters="cost &gt; 1"` returns error `Invalid filter format. Operators must have spaces on both sides.` Use `filters="cost > 1"` instead. Easy to miss when copy-pasting from HTML notes. Same for `<`, `>=`, `<=`.

**26. The pre-ship audit's "Offer URLs use /singapore/" regex has a leading-slash bug.**
Pattern `/(marbella|singapore|...)/offers/[^\s"\']+` captures `singapore/offers/...` (no leading slash), so any subsequent `startswith('/singapore/')` check fails 100% of the time even when URLs are correct. Fix: change the regex to `(/(?:marbella|singapore|...)/offers/[^\s"\']+)` with the slash inside the capture group, or use `re.findall(r'href="(/[^"]+)"' )` and filter for `/singapore/`. False-fail on valid files until patched.

**27. "Website Traffic Overview" replaces older "Traffic by source & medium" on Page I.**
Newer spec (May 2026): full-width card at the bottom of Page I containing (a) a 4-cell totals band in `var(--surface-2)` background (Users · Sessions · Engaged sessions · Avg time/session) and (b) a 10-column channel-group breakdown table below it (Default channel group · Users · New users · Sessions · Engaged sessions · Engagement rate · Avg time/session · Sessions/user · Bounce rate · Views/session). Data source: GA4 query with `sessionDefaultChannelGroup` dimension, ranked by sessions descending. Bounce rate uses pill colors: 🟢 <25%, 🟡 25–40%, 🔴 >40%. This replaces the older "Traffic by source & medium" 6-column table — both serve the same goal (eliminate the need to look at GA4 directly) but the channel-group breakdown is more useful at executive level.

**28. The "totals band" pattern is reusable for any large table.**
Used on Page I (Website Traffic Overview), Page VI (Market Efficiency). 4-cell grid in surface-2 background, rounded corners, sitting above the table. Each cell: a small uppercase label (10px, ink-3 color) and a large bold number (22px, ink color). Numbers carry `data-base` / `data-fmt` for date-filter scaling. Pattern:

```html
<div class="traffic-totals" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;padding:14px 16px;background:var(--surface-2);border:1px solid var(--line);border-radius:6px;">
  <div>
    <div style="font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--ink-3);margin-bottom:4px;">LABEL</div>
    <div style="font-size:22px;font-weight:700;color:var(--ink);" data-base="NNNN" data-fmt="int">N,NNN</div>
  </div>
  <!-- repeat 4× -->
</div>
```

When the number is monetary, wrap the `$` in a smaller inline span: `<div style="font-size:22px;..."><span style="font-size:14px;">$</span><span data-base="NNNN" data-fmt="int">N,NNN</span></div>`. The split keeps the dollar sign smaller and the number scalable.

**29. Page VI: "Device split" and "New vs returning users" canvases were empty placeholders.**
These were rendered as `<canvas>` elements but their builders never had data wired in (the GA4 device + new-vs-returning queries were skipped in earlier builds). Remove the entire `<div class="grid-2">` row at the bottom of Page VI. Keep the JS builders harmlessly — they use `if (el)` guards so they silently skip when the canvases are gone. Either delete the builders too, or leave them as no-ops (the latter is faster).

> **Update (Bodrum, Jun 2026):** if you DO have real device + new-vs-returning data (GA4 `deviceCategory` and `newVsReturning` pulls), **populate these canvases instead of removing them.** Bodrum kept the Page V device chart + Page VI device-split and new-vs-returning donuts, all wired to real GA4 numbers (device sessions `[mobile, desktop, tablet]`, new-vs-returning sessions `[new, returning]`). Only strip them when the data genuinely isn't available.

**30. `pill danger` is an undefined CSS class — use `pill bad`.**
The stylesheet defines `.pill.good`, `.pill.warn`, `.pill.bad`, `.pill.neutral` — there is **no `.pill.danger`**. Some reference HTMLs (incl. the Singapore source) carry `class="pill danger"` in the markup, which renders as an unstyled base pill (no red). When generating any pill (bounce rate, CVR, ROAS, market priority), emit `bad`, never `danger`. Audit: `grep -o 'pill [a-z]*' file.html | sort -u` — the only variants that should appear are `good`, `warn`, `bad`, `neutral`. If `danger` shows up, `sed -i 's/class="pill danger"/class="pill bad"/g'`. Suggested thresholds: bounce `<26%` good / `<50%` warn / else bad; CVR `≥1%` good / `≥0.5%` warn / else bad; ROAS `≥6x` good / `≥3x` warn / else bad.

**31. Sessions: daily-array sum vs. the aggregate one-row pull won't match exactly.**
GA4 returns a slightly different total when you sum a per-day `sessions` pull vs. pulling sessions as a single aggregate row (sampling/threshold differences). Bodrum: daily sum = 77,085 vs aggregate = 75,872. This is normal, not a bug. Convention (matches Marbella/Singapore): use the **aggregate one-row value for the Website-Traffic-Overview totals band**, and the **daily array for trends and the JS-computed totals** (CVR denominator, etc.). Don't try to force them equal.

**32. Offer count is property-specific — don't force 5 offers.**
The Singapore/Marbella offers page has 5 offers; Bodrum has **4** real ones (Plan Ahead Your Stay, Stay 3 Pay 2, Now Open / Brand Launch, Weddings), derived from the real offer landing pages + creative naming + Google campaign types. The offers table, the four Page III charts (`offer-rev`, `offer-bkg`, `offer-channel` Google/Meta arrays, `offer-trend` line datasets), and the `var offers = [...]` label array must **all carry the same N**. When N≠5, edit every one of them or the charts desync. Because GA4 has **no measured revenue-per-offer**, Page III is **modeled** (per the documented attribution model): spend is real (grouped by offer's creatives/campaigns), and revenue/bookings are allocated across offers by **real click share**, scaled to the documented 60.9% offer-contribution / 60.7% offer-booking share. **Label it "Modeled" in the card subtitle.** Same honesty rule applies to the Page IV conversion-path values (attribution split × real Google/Meta spend share) and the Page VI market-efficiency paid-spend column (real revenue, paid spend allocated by session share — say so in the subtitle).

**33. Creative images on non-Singapore builds: the sandbox blocks Instagram/Facebook CDNs.**
`scontent*.cdninstagram.com` and `*.fbcdn.net` are NOT in the bash network allowlist, so you **cannot** `curl`/download the thumbnails to base64-embed them the way the Singapore reference does. Options: (a) reference the **fresh** Meta CDN URLs directly in the `creatives` array `image:` field — they render in a browser immediately but Meta **expires them in ~24h**, after which the `img.onerror` handler hides them and the gradient fallback shows; or (b) re-pull + embed at client-ship time from an environment with network access. Always re-pull URLs on the same day you ship, and tell the user about the expiry. The creative section renders as a **table of rows** (`#creative-rows`, built by `buildCreatives()`) — add/remove rows freely; only `{fmt, offer, name, image, spend, impr, clicks, ctr}` are used (the per-creative `data` array in older objects is vestigial).

**34. Meta ad accounts can be MULTI-BRAND — ALWAYS filter to the property's own campaigns. (Bodrum, Jun 2026)**
The single most dangerous data-integrity trap found so far. The Meta account is often a shared agency account holding **many venue brands**, not just the METT hotel. Bodrum's `act_797332184222785` contained **six** brands: METT Bodrum, **Folie Bodrum**, Attiko, Isola, Moi Spa, Raise. An **account-level** daily pull silently sums ALL of them into "METT" spend.

Why it's insidious: the contaminated total **reconciles to the cent** against itself (file array sum == account-level pull == ad-set sum), so a naive "verify against live data" check **passes** while the number is wrong. Bodrum was inflated by Folie's ₺38,898 (€727) — 30% of Meta spend — surfacing as `IBRAM` / `Opening` / `Page Growth (Tourists)` ad sets (all WhatsApp "- WA" click-to-message, zero hotel-booking intent).

**Rule: every Meta (FA) query MUST filter to the property's campaigns.** Use `filters="adcampaign_name =@ METT"` (or the exact brand token, e.g. `=@ METT Bodrum`). This applies to the daily pull (#2), ad-set pull (#9), and per-creative pulls (#10/#11) — without it, daily arrays, the ad-set table, creative cards, offer-spend allocation, paid-spend KPI, and ROAS are all contaminated.

**Verification that actually catches it** (account-level reconciliation does NOT):
1. Pull `campaign_and_resource_get(resource_type="campaigns")` and read the full campaign list — if you see non-METT brand names, the account is shared.
2. Pull ad-set spend WITH the `adcampaign_name` dimension (field id is **`adcampaign_name`**, NOT `campaign_name` — the latter aliases to ad-set name in this connector) and confirm every row's parent campaign is a METT campaign.
3. Sum the METT-only campaigns and confirm it's < the account total when other brands are active.

Google Ads can have the same trap — but Bodrum's `2898288837` was clean (all three campaigns `SEM_METT` / `PMAX_METT` / `SEM_Wedding` are METT). Still verify with the campaign list every time. **GA4 is normally safe** (it's the hotel's own property/site); shared-account ad spend that points to WhatsApp/Page destinations never hits the hotel site, so GA4 revenue/sessions/channels stay clean — the contamination is spend-side only. When you remove a contaminating brand, keep the GA4-based paid revenue/booking split as-is and let ROAS *rise* (you're dividing real revenue by the now-correct, smaller spend).

**35. Default the report to the latest month, not "All data". (Barcelona, Jun 2026)**
Clients open the dashboard expecting the CURRENT reporting period, not the entire data history. Default the date range to **"This month" anchored to the last day in `dates[]`** (`_dataEnd`) — e.g. data through Jun 14 opens on Jun 1–14. Set `state.activePreset = 'this-month'` and compute `state.startDate`/`state.endDate` from `_dataEnd`. Two anchoring rules:
- Anchor to **`_dataEnd`**, never `new Date()` — the viewer's real clock may be months ahead of the data, which would default to an empty range.
- Never hardcode the month. Anchoring to `_dataEnd` means every future refresh **auto-advances** the default with zero edits.

The "All data" preset stays available for the full-window view. ⚠️ Changing the default from full-window to a sub-range EXPOSES Lessons 36 and 37 — both were dormant only because the old default (full window) happened to match the static HTML. Read them before shipping.

**36. CRITICAL — `updateKPIs()` must run on INITIAL LOAD, not only on filter Apply. (Barcelona, Jun 2026)**
The highest-impact render bug of the session, and it stays hidden until the default range changes. In every property build, `updateKPIs()` (the function that rewrites all KPI cards from `getScaledData()` and scales the `data-base` table cells) is called **only inside `commitDates()`** — the date-picker Apply handler. The `init()` function just calls `initPage('overview')`, which runs the page's chart builder but **does NOT touch the KPI cards**. So on first paint the KPI cards keep whatever **static HTML values** were baked into the file.

This was invisible for every prior build because the default range was "All data" = the full window, and the static HTML values *were* the full-window totals — so they happened to match. The moment you default to a sub-range (Lesson 35), the date label correctly reads "1–14 Jun" while every KPI card still shows the full-window total (Barcelona: €273,781 revenue / €28,335 spend / 8.0× ROAS instead of June's €28,573 / €4,689 / 5.0×). The numbers look authoritative and are completely wrong.

**Fix:** call `updateKPIs()` once during `init()`, AFTER committing the default range into `state`, and BEFORE `initPage('overview')`:
```javascript
// init() — default to latest month, then render
applyPreset('this-month');
state.startDate = state.tempStart; state.endDate = state.tempEnd;
// sync the visible date labels (Lesson 37)
document.getElementById('date-value').textContent = fmtDateRange(state.startDate, state.endDate);
var _id = daysBetween(state.startDate, state.endDate);
document.getElementById('period-sum').textContent = _id === 1 ? '1 day' : _id + ' days';
document.getElementById('filter-indicator').innerHTML = 'Showing this month \u00B7 ' + fmtDateRange(state.startDate, state.endDate);
updateKPIs();          // ← the missing call: recomputes every KPI card + scales all data-base cells for the default range
initPage('overview');  // charts only — never calls updateKPIs itself
```
`initPage()` and the page builders **never** call `updateKPIs()` — it is always a separate, explicit call. Whatever the default range is, the load path and the Apply path must produce identical KPI cards.

**37. When you default to a sub-range, ALL the static header labels are frozen — sync them on load too. (Barcelona, Jun 2026)**
Separate from the KPI cards (Lesson 36): the report's date strings are baked into the HTML and only rewritten by the picker's Apply handler. Default to the latest month without syncing them and the header lies — the live-pill, the date-range button (`#date-value`), the "Showing … data" strip (`#filter-indicator`), the calendar selection (`#cal-selected`), the period-day count (`#period-sum`), and the **active-preset highlight** all keep their "Mar 1 – May 31 / All data" values while the KPIs (once Lesson 36 is fixed) show June. Two halves of the fix:
- **Static HTML:** rewrite the baked default strings to the latest-month range, move the `active` class off the "All data" preset button onto the "This month" button, and update the "All data" preset's right-aligned sublabel to the true full window (`Mar 1 – Jun 14`).
- **Runtime (in `init()`):** set `#date-value`, `#period-sum`, `#filter-indicator` from `fmtDateRange(state.startDate, state.endDate)` (shown in the Lesson 36 snippet), and call `applyPreset('this-month')` so `renderPresetActive()` + `renderCalendar()` highlight the right preset and sync `#cal-selected`.
- **Live-pill exception:** JS does NOT touch the top live-pill. It should show the **full data window** (`Mar 1 – Jun 14, 2026`), not the selected month — fix it in static HTML only. (The `Updated DD MMM YYYY` timestamp is still build-time; Lesson 21.)

**38. Verify the load render headlessly before shipping — don't make the client catch it. (Barcelona, Jun 2026)**
Lessons 36/37 pass `node --check` (syntax is fine) and pass `grep` (the wrong values are still "valid" numbers), so neither catches them. The only reliable pre-ship gate is to actually run `init()` against a stubbed DOM and read back what the KPI cards become. Extract the `<script>`, stub `document`/`window`/`Chart`, force `document.readyState='complete'` so `init()` runs, then read the values back. Two gotchas that cause **false negatives**:
- Top-level chart config (`Chart.defaults.font.family = …`) throws on a plain stub and prevents `init()` from ever running. Make `Chart` an **auto-vivifying Proxy** (every property access returns another callable Proxy) so setup can't throw.
- `setKpi(id, html)` writes to a **`.value` child** (`el.querySelector('.value').innerHTML = …`), so a stub whose `querySelector` returns `null` records nothing and every card reads "(unset)". Make the stub's `querySelector('.value')` return a **recording child node**.

Then assert `kpi-total-rev` equals the **selected-range** total (e.g. June €28,573), not the full-window total. If it shows the full window, Lesson 36 isn't actually fixed. A ready-to-run harness is in `scripts/runtime_smoke.js`.

**39.5 / 40. A property is a GROUPING, not a column value. (METT.html, Jul 2026)**
Building the cross-property table, the first instinct is a `Property` column: `METT Marbella | META | …` / `METT Marbella | Total | …`. This is wrong two ways and the user will call it out as "looks weird":
- Repeat the name on every row → the same hotel appears 2-3× and reads like 3 hotels.
- Print it only on the first row → the total row's first cell is **empty**, and blank cells under a floating name is the visual tell that the structure is broken.

Neither is fixable with spacing. Both are symptoms of forcing a *grouping key* into a *column*. Three escalating fixes, in the order they were tried — **skip to the third**:
1. ~~Blank the duplicate + add a spacer row~~ — still leaves holes.
2. ~~Group-header band spanning `colspan=8` above each group~~ — better, but adds a beige band that fights the navy header.
3. **One table per hotel; the hotel name lives in the navy `<thead>` as the first `<th>`** (where the useless `Channel` header was), with the currency chip beside it. The header does double duty — names the group AND labels the columns. Zero empty cells, zero repeated names, `gap:15px` between tables does the separating.

Alignment across separate tables: `table-layout:fixed` + a locked first-column width (`th.th-name{width:210px}`), or the four tables each self-measure and the columns wander.

**41. Verify JS-built markup by running it, not by reading it. (METT.html, Jul 2026)**
When the whole page is built from template literals, `node --check` only proves the *template* parses — it says nothing about what the DOM becomes. Cheap gate: extract the `<script>`, cut everything from `function render(` onward (that's the DOM-dependent tail), append `console.log(propTable('marbella','2026-05'))`, and run it in node. Pure builder functions need no DOM stub and you see the real HTML in one second. (For Deliverable A, where `init()` must run, use the full stub harness — Lesson 38.)

**42. Deleting a section means deleting its CSS, its builder, and its data map. (METT.html, Jul 2026)**
Five "remove X" requests in a row (Summary block, By Property cards, section labels, method note) each left orphans: dead `.kpi*` / `.card*` / `.chan*` rules, an unused `propCard()`, a `LOC` map, an `innerHTML` write to a node that no longer existed, and an empty `@media` block. None throw errors — they just rot. After every removal run the **class-parity audit** (every class in markup exists in CSS, and flag CSS classes nothing uses) and grep the removed identifiers to 0. File went 45.9 KB → 37.2 KB purely from cleaning up after removals.

**43. Don't sum across currencies — and prefer deleting the row to inventing an FX rate. (METT.html, Jul 2026)**
The one-pager's Summary band added Singapore's USD to three properties' EUR. Adding `≈` and a "directional only" caveat is **not** a fix; it's a wrong number with an apology attached. When asked to convert, the honest blocker is that there's no locked USD→EUR rate the way TRY 53.5 is locked for Bodrum — so **ask for the house rate, don't grab mid-market off the web and bake it in**. Here the user's own answer was better: delete the cross-property aggregate entirely. Every figure then sits inside one hotel's block in that hotel's own currency and nothing is ever added across currencies. If a EUR total is ever wanted back, get the rate locked in this file first.

## Things to remove from older reference HTMLs

Older versions of these dashboards (pre-May 2026) had several boilerplate elements that have since been removed. When starting from an older reference, strip these out:

| Location | What to remove | Replacement |
|---|---|---|
| Page I tab name | "Executive overview" | "Overview" |
| Page I heading | `<h2>Executive overview</h2>` | `<h2>Overview</h2>` |
| Page I subtitle | `<p class="sub">Commercial performance across paid, organic, and direct channels...</p>` | (nothing — delete the `<p>`) |
| Page I bottom (older "Traffic by source & medium" 6-col table) | The `<div class="card">` containing `<h3>Traffic by source &amp; medium</h3>` | Replace with **Website Traffic Overview** (4-cell totals band + 10-col channel-group table). See section "Website Traffic Overview" below. |
| Page V subtitle | `<p class="sub">End-to-end funnel from first session to completed booking...</p>` | (nothing) |
| Page V caption below Top Landing | `<p>Two issues to fix: a malformed booking URL...</p>` | (nothing) |
| Page V insight box | `<div class="insight">The biggest funnel issue here is cross-domain attribution loss...</div>` | (nothing) |
| Page V caption below Top Viewed | `<p>Per-page booking revenue is not visible in GA4...</p>` | (nothing) |
| Page V geo table (older 8-col version) | `<thead>` with Country · City · Users · Sessions · Engagement · Bookings · Revenue · CVR | Replace with **10-col version**: insert Avg time/session and Bounce rate (with pill colors) between Engagement and Bookings. Sort by bookings descending. |
| Page VI bottom (empty charts) | The `<div class="grid-2">` row containing `<h3>Device split</h3>` and `<h3>New vs returning users</h3>` | (nothing — delete the entire row; JS builders stay as no-ops via `if (el)` guard) |
| Page VI "Top markets by revenue" + "by bookings" cards | Both cards as bare siblings of `<section>` | Wrap them in `<div class="grid-2">...</div>` (frequent regression spot — see Lesson 23) |
| Calendar sidebar | `<button data-preset="ytd">Year to date</button>` and `case 'ytd':` switch arm | (delete both) |
| Top nav | `<button data-tab="action"><span class="num">VIII</span>Recommendations</button>` | (delete) |
| HTML body | Entire `<section class="page" id="page-action">...</section>` block | (delete) |
| pageBuilders registry | `action: function(){}` or `action: buildAction` | (delete the entry) |

After cleanup, run the audit. JS syntax must validate, audit must be 9/9 PASS.

## Deliverable B — `METT.html` (cross-property one-pager)

A single page covering **all four properties** for the **last 3 months**, month-filtered. Not a replacement for the property reports — an at-a-glance roll-up for the client. Built Jul 2026; this section is the spec.

### Scope of data (deliberately narrow)

Only these metrics, per channel (Meta, Google), per hotel, per month:

`Impressions · Clicks · Cost per Click · Ad Spend · Total Revenue · Rooms Booked · ROAS`

plus a **Total** row per hotel. **No `Target` column** — the client's source sheet has one; it is explicitly removed. No charts, no creatives, no funnel, no geo. If asked to add a section, ask whether it belongs here or in the property report.

### Page structure (final, after 8 rounds of user edits)

```
masthead  → METT wordmark (inlined PNG) │ divider │ "METT Hotels / Paid Media Performance"
             right: live-pill (current month) · "Data through DD MMM" · source chips
filter    → sticky bar: calendar icon + full date range │ month segments [May – 26][Jun – 26][Jul – 26]
indicator → "Showing May – 26 · all four properties"
tables    → 4 × per-hotel table, gap:15px
footer    → "METT HOTELS — Marbella · Barcelona · Bodrum · Singapore" / prepared by 3rdScreen
```

Per-hotel table:

```
┌ navy thead ─────────────────────────────────────────────────────────┐
│ METT MARBELLA [EUR] │ IMPRESSIONS │ CLICKS │ COST/CLICK │ … │ ROAS  │
├─────────────────────┼─────────────┼────────┼────────────┼───┼───────┤
│ [Meta]              │   1,208,551 │ 26,509 │      €0.12 │ … │ 43.92×│
│ [Google]            │     226,058 │ 13,119 │      €0.61 │ … │ 24.81×│
│ TOTAL               │   1,434,609 │ 39,628 │      €0.28 │ … │ 13.47×│
└─────────────────────────────────────────────────────────────────────┘
```

### Locked rules for B

- **Naming: "METT HOTELS" only.** No "METT Hotels & Resorts" anywhere — title tag, masthead, footer.
- **Logo**: the client wordmark, inlined as base64 so the file stays self-contained. Crop to the glyph bbox, recolor to `--ink` (#0E2340), alpha from luminance so it drops on any background. ~20 KB at 720px wide. Never link an external asset.
- **Month labels always carry the year: `Month – YY`** (`May – 26`, not `May`). Applies to the segments, live-pill, and filter indicator. The long date range under the calendar icon keeps the full form (`1 – 31 May 2026`) since it's an explicit window, not a label.
- **No cross-currency aggregation** (Lesson 43). Each hotel's figures stay in its own currency; there is no portfolio/summary band.
- **Partial months**: label them (`1 – 14 July 2026 (partial)`) in the date range. The user removed the prose caveat — flag partial-month reads in chat instead.
- **`table-layout:fixed`** + `th.th-name{width:210px}` so all four tables share a column grid.
- Design tokens (palette, fonts, chips, pills) are **shared with Deliverable A** — reuse them verbatim; don't invent a second visual language.

### Mobile (explicit requirement)

Three breakpoints: **1080px** (relax gaps) → **760px** (compact sticky filter, tighter type, `min-width:760px` tables scroll with a "swipe to see all columns" hint) → **420px** (single-column). The month segments stay **sticky at the top** so switching months never means scrolling back up.

### Build sequence for B

1. Pull daily `date,impressions,clicks,cost` per property from **FA** and **AW** (METT-scoped filters — same as Deliverable A), and `date,totalRevenue,transactions` from **GAWA**. Start `2026-05-01`, end = today; the actual data end is whatever comes back (Jul 2026 build: 14 Jul).
2. All 12 queries can be **submitted in parallel** before polling any (`data_query` → `schedule_id` → `get_async_query_results(compress=True)`).
3. Aggregate to month × property × channel in Python. Apply the **same locked attribution model as Deliverable A**: paid revenue = 82.5% of GA4 revenue, paid bookings = 82.3% of transactions, Google:Meta split 59:41 (**Bodrum 76:24**). Bodrum monetary ÷ **53.5** → EUR.
4. Emit a `data.json`, inject it into the HTML template as a single `const DATA = {...}` blob. Render is pure client-side from that blob — one `render(month)` repaints tables + all header labels.
5. Validate: `node --check` the script, **run `propTable()` in node** (Lesson 41), class-parity audit (Lesson 42), grep month labels for a missing year.
6. `present_files(["/mnt/user-data/outputs/METT.html"])`.

### Working files (Jul 2026 build)

- `/home/claude/build.py` — raw pulled data pasted inline + month aggregation → `data.json`
- `/home/claude/gen.py` — HTML template + `__DATA__` / `__LOGO__` injection
- `/home/claude/logo_b64.txt` — base64 wordmark

Rebuilding from a new pull = update the pasted blocks in `build.py`, rerun both. **Never hand-type the arrays.**

## Files in this skill

- `SKILL.md` — this file
- `METT.html` — **Deliverable B**, the cross-property one-pager (see its section above)
- `README.md` — quick reference and property currency table
- `reference/METT_Marbella_reference.html` — **gold-standard reference**, post-May-2026 cleanup. EUR, 71 days data through May 10, calendar bounds-clamped, 7-tab nav (no Recommendations), Traffic-by-source on Page I, Geo Performance with avg time + bounce on Page V, square 4-per-row creative cards with fresh real thumbs.
- `reference/METT_Singapore_reference.html` — Singapore equivalent (SGD→USD)
- `scripts/build_property.py` — parameterized build script
- `scripts/pre_ship_audit.py` — **automated 9-check audit. Run on every build before shipping. Handles any month, not just April.**
- `scripts/runtime_smoke.js` — Node-side smoke test for the embedded JS
- `scripts/data_pull_template.md` — exact query templates for the Supermetrics calls

## Output convention

Deliverable A: `/mnt/user-data/outputs/METT_<Property>.html`
Deliverable B: `/mnt/user-data/outputs/METT.html` (exact filename — the user asked for it by name)

Deliverable A file path: `/mnt/user-data/outputs/METT_<Property>.html`
File name uses the property's clean name (no spaces, capitalized): `METT_Marbella.html`, `METT_Singapore.html`, `METT_Bodrum.html`, etc.

Always end the build with `present_files(["/mnt/user-data/outputs/METT_<Property>.html"])` and a brief summary of the property's commercial picture (total revenue, paid spend, ROAS, top finding).

## Pre-ship checklist (run every single time)

### Deliverable B (`METT.html`) — short checklist

- [ ] `node --check` on the extracted `<script>` returns 0
- [ ] `propTable()` executed in node and the emitted HTML eyeballed (Lesson 41)
- [ ] Class-parity audit clean, and **no orphaned CSS/JS from removed sections** (Lesson 42)
- [ ] Every month label reads `Month – YY` — grep for a bare `May`/`Jun`/`Jul`
- [ ] Static header strings match the default month (live-pill, date-value, filter indicator, active segment)
- [ ] **No cross-currency totals anywhere** (Lesson 43)
- [ ] No `Target` column; naming is **METT HOTELS** only (0 hits for "Hotels & Resorts")
- [ ] Logo is inlined base64 — 0 external asset requests
- [ ] Renders at 380px wide: filter sticky, tables scroll, nothing overflows

### Deliverable A (`METT_<Property>.html`) — full checklist

Before calling `present_files`:

**Automated:**
- [ ] `python3 scripts/pre_ship_audit.py /path/to/METT_<Property>.html` returns 9/9 PASS
- [ ] JS syntax: `node --check` the extracted `<script>` block returns 0

**Date filter & calendar:**
- [ ] **Initial-load default test (Lessons 35–38)**: open the file fresh — the date button must read the **latest month** (e.g. `1 – 14 Jun 2026`), the "This month" preset must be the active one, the "Showing this month · …" strip must match, AND the Page I KPI cards must show that month's totals (NOT the full-window totals). If the label says June but the cards show the full window, `updateKPIs()` isn't running on load. Confirm headlessly with `scripts/runtime_smoke.js` (asserts `kpi-total-rev` = the selected-range total).
- [ ] **Date filter test (full)**: pick "Last 7 days" → verify Page I KPIs shrink, Page II Channel Summary numbers shrink proportionally, **and Page VII Creative cards re-rank with new spend/impressions/CTR values that match the 7-day window**
- [ ] **Calendar preset test**: click "Last 14 days" preset → verify the date range reads as `[data_end - 13 days] → [data_end]`, NOT a hardcoded older range. Same for "All data" — must extend to the last day in the dates array
- [ ] **Calendar bounds test**: open the calendar → in the month AFTER your `_dataEnd`, days are muted/disabled. Try clicking the next-chevron when at the data-end month → button is greyed out, no nav happens. Same for prev-chevron at month BEFORE `_dataStart`
- [ ] **NO YTD preset**: the sidebar should NOT have a "Year to date" button
- [ ] **Calendar interaction test**: click the calendar → pick day 1, then day 23, verify range highlights and Apply commits the range

**Structure & content:**
- [ ] Top nav has **exactly 7 tabs** — no "Recommendations" / Tab VIII
- [ ] Page I tab name is **"Overview"** (not "Executive overview")
- [ ] Page I has **9 KPI cards in a 3×3 grid** (`kpi-grid cols-9`), with **Website Conversion Rate** as the 9th card. Subtitle reads "X bookings / Y sessions" with real numbers (not placeholders)
- [ ] Total Revenue subtitle "X days · Y bookings" — Y must equal `BASELINE.totalBookings` (watch for drift after data extensions)
- [ ] Page I has the **Traffic by source & medium** table at the bottom (full width, 6 columns)
- [ ] Page V has the **Geo Performance** table with 10 columns (including Avg time/session + Bounce rate)
- [ ] Page V has NO subtitle paragraph, NO caption below Top Landing, NO insight box, NO caption below Top Viewed
- [ ] Page I has NO subtitle paragraph

**Creative tab:**
- [ ] **Creative tab visual test**: open the file in a browser, click the Creative tab — verify 4-8 distinct images render in a 4-column grid (no identical fallback SVGs). If all 8 cards look identical → thumbnails are stale, re-pull
- [ ] **No fake imagery**: NEVER replace creative thumbnails with generated branded SVGs as a workaround for expired URLs. The cards must show real ad images from Supermetrics.

**Property hygiene:**
- [ ] Footer shows correct GA4/Meta/Google account IDs for THIS property
- [ ] All offer URLs match `metthotelsandresorts.com/<property>/offers/...` pattern
- [ ] Page V top pages all start with `/<property>/` prefix (no `/marbella/` leaks if not Marbella)
- [ ] Header `Updated DD MMM YYYY · HH:MM UTC` timestamp manually bumped to today's date


---

# FEATURE: Calendar "Compare" mode (period-over-period) — canonical, port to ALL properties

Added first on Barcelona (Jul 2026). GA4-style comparison in the date-picker: a **Compare**
toggle + five modes, a second (blue) highlighted range in the calendar, and %-change chips
on the nine Overview KPI cards. **Defaults OFF**, so the static Overview HTML is unchanged and
`mett_layout_audit.py` still passes (it only fingerprints the Overview grid, never the calendar/CSS).

## Behaviour
- Toggle lives in the calendar popover, below the two month grids, above the footer.
- Modes (chips): **Previous period**, **Prev period (day of week)**, **Previous year**,
  **Prev year (day of week)**, **Custom**.
- When ON + Apply: the 9 Overview card deltas become `▲/▼ X.X% vs <compare range>`
  (green up / red down / grey flat). When OFF: canonical static deltas are restored.
- Comparison range with no data (e.g. prev-year before Mar 2026) → renders
  `no comparison data for period` instead of a misleading %.
- Compare range is highlighted in the calendar with a blue underline (`.cmp-range`/`.cmp-edge`),
  distinct from the gold main range.
- **Custom** mode: calendar clicks build the *comparison* range (blue) instead of the main range
  (`state.pickTarget='compare'`); to edit the main range again, pick any preset/other mode first.

## Compare-range math (definitions — keep identical across properties)
- `prev-period`: contiguous block of equal length ending the day before start.
  `ce = start-1; cs = ce-(N-1)`.
- `prev-period-dow`: as above, then shift the block back `d2 = ((cs.getDay()-start.getDay())%7+7)%7`
  days so `cs` lands on the **same weekday** as `start`. (Direction matters — shifting by
  `(start-cs)` instead of `(cs-start)` is WRONG; it lands on the opposite weekday.)
- `prev-year`: same calendar dates, `year-1`.
- `prev-year-dow`: `prev-year`, then nudge `±3` days to align `cs` weekday to `start` weekday.

## Port checklist (10 edits — all inside the single `<script>`/`<style>`, self-contained)
1. **CSS** after `.cal-btn.primary:hover {…}` — the `.cmp-*` block (switch, modes, chips,
   `.cal-day.cmp-range/.cmp-edge`). Compare accent colour `#5b8def`; up `#1a8f5a`, down `#c0392b`.
2. **HTML** — insert `.cmp-panel` immediately before `<div class="cal-footer">`.
3. **state** — add: `compareEnabled:false, compareMode:'prev-period', compareStart:null,
   compareEnd:null, pickTarget:'main'`.
4. **helpers** after `addDays()` — `computeCompareRange`, `rangeTotals`, `cmpChip`,
   `setCmpDelta`, `_origDeltas`+`snapshotDeltas`, `updateCompareUI`.
5. **renderCalendar()** top — recompute compare range for non-custom modes from
   `tempStart||startDate` etc., then `updateCompareUI()`.
6. **renderMonthGrid** cell classes — add `.cmp-edge`/`.cmp-range` when in compare range and not muted.
7. **day click handler** — before the main-range logic, if `compareEnabled && compareMode==='custom'
   && pickTarget==='compare'` build the compare range and `return`.
8. **updateKPIs()** end — if compare on, `rangeTotals(compareStart,compareEnd)` and `setCmpDelta`
   on the 9 Overview ids; else restore `_origDeltas` (kpi-total-bkg, paid-rev, paid-bkg, roas, cpb, aov).
   (total-rev/total-spend/cvr are re-set descriptively earlier, so only those 6 need snapshot/restore.)
9. **init()** — wire `#cmp-switch` click (flip `compareEnabled`, set `pickTarget`, `renderCalendar`)
   and `.cmp-mode` clicks (set `compareMode`; custom→clear compare range + `pickTarget='compare'`;
   auto-enable compare; `renderCalendar`). Call `snapshotDeltas()` once, right before the first
   `updateKPIs()` in the initial-render block.
10. **commitDates()** — when compare on, append `vs <compare range>` to the `#filter-indicator` HTML.

## Which cards get compare deltas
`kpi-total-rev, kpi-total-bkg, kpi-paid-rev, kpi-paid-bkg, kpi-total-spend, kpi-roas, kpi-cpb,
kpi-aov, kpi-cvr`. Compare metrics come from real daily arrays (same 0.825/0.823 attribution as
Overview), never modeled/scaled — so % change is exact and traceable.

## Validation (add to pre-ship for any property carrying Compare)
- `node --check` the extracted `<script>` (must pass).
- `mett_layout_audit.py` still PASS (compare defaults off → Overview static HTML untouched).
- Headless integration (Node DOM stub that stores `addEventListener` handlers so `.click()` fires them;
  stub `Chart` as an auto-returning Proxy, `setInterval/Timeout` as no-ops, `querySelector('.tab.active')`→null):
  fire `#btn-date-picker`→`#cmp-switch`→`#cal-apply`; assert a Overview delta contains a `cmp-chip`
  and `vs <range>`. Switch modes via `.cmp-mode[data-cmp=…]`. Toggle off → canonical delta restored.
  jsdom `runScripts:'dangerously'` HANGS on the chart/CDN code — use the lightweight Proxy stub instead.
- Unit-check `computeCompareRange` for a known range (e.g. Jul 1–26 2026, start=Wed): prev-period
  → Jun 5–30; prev-period-dow → Jun 3–28 (Jun 3 = Wed); prev-year → 2025-07-01..26; each length N.

## Lesson
- The audit only checks the Overview KPI grid; new calendar/CSS classes are safe **as long as
  Compare defaults OFF** and the 6 copy-checked cards' canonical static deltas are preserved
  (snapshot on init, restore when compare off). Never ship Compare defaulting ON.
