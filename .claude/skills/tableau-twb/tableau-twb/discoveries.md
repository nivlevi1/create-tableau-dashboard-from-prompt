# Tableau TWB Generation — Session Discoveries

Lessons learned while generating `NIS_Forex_Dashboard.twb` programmatically.
Each entry documents the symptom, root cause, and fix.

---

## 1. Error 6A063CF5 — Dashboard Size Validation Failure

**Symptom:** Tableau Desktop shows "Internal Error 6A063CF5" immediately on open.

**Root cause (from Tableau logs):**
`logic-assert` failure in `DashboardSizePresModelBuilder.cpp:180` — `CheckSizeValidity(minWidth, minHeight, maxWidth, maxHeight, sizeMode)` returned false.

Two problems in the `<size>` element:
1. `minheight` and `maxheight` were different values (`900` vs `1500`) — Tableau requires `min == max` for fixed-size dashboards.
2. `sizing-mode='fixed'` is **not a valid attribute** on `<size>` in generated TWBs.

**Broken XML:**
```xml
<size maxheight="1500" maxwidth="1500" minheight="900" minwidth="1500" sizing-mode="fixed" />
```

**Fixed XML:**
```xml
<size maxheight="1500" maxwidth="1500" minheight="1500" minwidth="1500" />
```

**Rule:** For a fixed-size dashboard, set all four size attributes to the same value. No additional attributes. The standard pattern from the skill reference is `min=max` on both axes.

---

## 2. Error 6A063CF5 — Duplicate `<column>` and `<column-instance>` in datasource-dependencies

**Symptom:** Same Internal Error 6A063CF5 (appears identical to the size error from the outside).

**Root cause:**
In KPI "% vs" worksheets, `val_field` and `pp_field` were set to the same calculated field (e.g. both = `[Calculation_1007]`). The deps-building loop iterated over `[val_field, pp_field, pn_field, ap_field, an_field]` without deduplication, inserting the same `<column>` and `<column-instance>` twice into `<datasource-dependencies>`.

**Broken pattern:**
```xml
<datasource-dependencies datasource="...">
  <column name="[Calculation_1007]" ... />
  <column name="[Calculation_1007]" ... />   <!-- duplicate! -->
  <column-instance name="[usr:Calculation_1007:qk]" ... />
  <column-instance name="[usr:Calculation_1007:qk]" ... />  <!-- duplicate! -->
  ...
</datasource-dependencies>
```

**Fix:** Deduplicate with a `seen` set before adding any field to deps or encodings:
```python
seen = set()
for f in [val_field, pp_field, pn_field, ap_field, an_field]:
    if f in seen:
        continue
    seen.add(f)
    # ... add column and column-instance
```

Apply the same deduplication to the `<encodings>` block inside the pane.

---

## 3. Arrow Calcs Must Use `derivation='User'` and `usr:` Prefix (§25.11)

**Symptom:** KPI cards may render blank or incorrectly; can also contribute to 6A063CF5.

**Root cause:**
Arrow calculated fields (`IF AGG(...) > AGG(...) THEN "▲" END`) return a **string**, so they were treated as dimensions with `derivation='None'` and `[none:...:nk]` column-instance names. However, because their formulas **reference other aggregate calcs** (e.g. `SUM(IF ... END)`), they are implicitly aggregate — Tableau cannot evaluate them with `None` derivation.

**Rule (§25.11 in programmatic-twb-learnings.md):**
> Any calculated field returning a string that **contains or references** SUM/AVG/COUNTD etc. is an aggregate calc. Even though `datatype='string'`, the `column-instance` MUST use `derivation='User'` with the `usr:` prefix.

**Broken:**
```xml
<column-instance column="[Calculation_1009]" derivation="None"
                 name="[none:Calculation_1009:nk]" pivot="key" type="nominal" />
```
```xml
<run><![CDATA[<[ds].[none:Calculation_1009:nk]>]]></run>
```

**Fixed:**
```xml
<column-instance column="[Calculation_1009]" derivation="User"
                 name="[usr:Calculation_1009:nk]" pivot="key" type="nominal" />
```
```xml
<run><![CDATA[<[ds].[usr:Calculation_1009:nk]>]]></run>
```

The suffix stays `:nk` (nominal key / discrete). Only the derivation prefix changes from `none:` → `usr:`.

---

## 4. `sizing-mode` Is Not a Valid `<size>` Attribute

**Symptom:** Part of Error 6A063CF5 (see entry #1 above).

**Detail:**
The Python helper used `**{'sizing-mode': 'fixed'}` when building the `<size>` element. Tableau's XSD does not declare `sizing-mode` on `<size>` — it causes the internal size validator to receive an unexpected mode value and assert-fail.

**Rule:** The `<size>` element accepts only `maxheight`, `maxwidth`, `minheight`, `minwidth`. No mode attribute. Fixed size = all four equal.

---

## 5. CSV (`textscan`) Connection Pattern

**Confirmed working structure** for a local CSV file:
```xml
<datasource caption="NIS Exchange Rates" inline="true"
            name="textscan.nis_forex_exchange" version="18.1">
  <connection class="textscan"
              directory="C:\path\to\folder"
              filename="NIS_Exchange_Rates.csv"
              password="" server="">
    <relation name="NIS_Exchange_Rates#csv"
              table="[NIS_Exchange_Rates#csv]" type="table">
      <columns header="yes" outcome="7">
        <column datatype="date"     name="Date"       ordinal="0" />
        <column datatype="real"     name="USD"        ordinal="1" />
        <column datatype="real"     name="GBP"        ordinal="2" />
        <column datatype="real"     name="JPY_100"    ordinal="3" />
        <column datatype="real"     name="EUR"        ordinal="4" />
        <column datatype="real"     name="CHF"        ordinal="5" />
        <column datatype="datetime" name="updated_at" ordinal="6" />
      </columns>
    </relation>
  </connection>
  <aliases enabled="yes" />
  <!-- column definitions and calculated fields follow -->
</datasource>
```

Key points:
- Connection class is `textscan` (not `federated`, not `text`).
- `directory` = folder path, `filename` = file name only (not full path).
- Tableau converts `.` to `#` in relation/table names: `NIS_Exchange_Rates.csv` → `NIS_Exchange_Rates#csv`.
- `<columns header="yes" outcome="N">` inside `<relation>` declares column types upfront.
- `<aliases enabled="yes" />` must come before any `<column>` elements in the datasource.

---

## 6. Zone layout — `zone-style` Must Be Last Child (§28.1)

**Rule (already in skill, confirmed in practice):**
In any `layout-basic` or `layout-flow` container zone, `<zone-style>` must be the **last** child element — after all `<zone>` children. Placing it first causes D2E8DA72 (`element 'zone' is not allowed for content model`).

**Pattern used:**
```python
def add_card_style(zone, margin='6'):
    # called AFTER all child zones have been appended
    zs = sub(zone, 'zone-style')
    sub(zs, 'format', attr='background-color', value='#FFFFFF')
    sub(zs, 'format', attr='margin', value=margin)
```

---

## 7. Text Zones in Dashboard Header

**Confirmed working structure** for a text label zone in a dashboard:
```xml
<zone id="4" h="3600" w="25000" x="0" y="0" type-v2="text">
  <formatted-text>
    <run fontname="Tableau Book" fontsize="10" fontcolor="#666666">Label text</run>
  </formatted-text>
  <zone-style>
    <format attr="background-color" value="#EAE4DA" />
  </zone-style>
</zone>
```

`<formatted-text>` is a direct child of the zone (not wrapped in anything). `<zone-style>` comes last.

---

## 8. Five-Phase TWB Generation Workflow

Phases followed in this session:

| Phase | Description | Gate |
|-------|-------------|------|
| 1 | Requirements gathering — data source, KPIs, chart types, filters, design | User confirms |
| 2 | ASCII wireframe — layout, zone hierarchy, section sizing | User approves |
| 3 | Python generator script → `.twb` XML | Automatic after gate 2 |
| 4 | `validate_twb()` — duplicate zone IDs, missing `simple-id`, zone name cross-ref | Must output `Validation PASSED` |
| 5 | Handoff — file path, worksheets list, testing checklist, iterate on Desktop feedback | Deliver to user |

**Key iteration pattern:** User opens in Tableau Desktop → reports error code or log detail → trace root cause in generator → fix → regenerate → re-validate → re-deliver.

---

## 9. Error Code Reference (Session Summary)

| Code | Cause in this session | Fix |
|------|-----------------------|-----|
| `6A063CF5` | `min != max` in `<size>` element OR duplicate `<column>` in `<datasource-dependencies>` | Set all four size values equal; deduplicate deps with a `seen` set |
| `D2E8DA72` | `<zone-style>` not last child; wrong `<aliases>` placement; invalid attrs | Follow element ordering rules |
| `A1E47F55` | `relative-date` filter on same field as shelf; `include-future="false"` | Use boolean calc filter instead |
| `018B7D29` | Custom SQL without `<metadata-records>` | Add metadata-records for every Custom SQL relation |
| `2805CF18` | Empty `<cards />` or empty `<viewpoint />` in window | Include full cards structure |
