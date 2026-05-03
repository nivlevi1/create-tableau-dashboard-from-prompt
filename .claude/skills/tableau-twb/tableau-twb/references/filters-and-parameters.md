# Filters, Parameters, and Quick Filters

Authoritative reference for Tableau TWB/XML filter and parameter patterns used in programmatic and template-aligned workbooks. Element ordering within `<view>` follows [xml-schema-and-structure.md](xml-schema-and-structure.md) (`datasources` → `datasource-dependencies` → `filter*` → `shelf-sorts?` → `slices?` → `aggregation`). Error codes: [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md). Deep dives: [programmatic-twb-learnings.md](programmatic-twb-learnings.md).

**Sources consolidated:** KPI Dashboard Template filters, Superstore KPI Overview formatting/filters, Date filter on dashboard pattern.

---

## Filter Hierarchy

Processing and placement follow this order:

1. **Extract-level** — Inside `<extract>` / connection: restrict data before the extract (or hyper) is materialized.
2. **Shared-view** — Under `<shared-view>` at workbook level: filters shared across worksheets using the same datasource; use `context='true'` where noted below.
3. **Worksheet** — Inside each worksheet’s `<view>`: filters scoped to that sheet.
4. **Slices (quick filters)** — Immediately after worksheet `<filter>` elements, before `<aggregation>`: expose filters as quick filter cards and drive dashboard filter zones.

In XML, **extract** filters live under the datasource’s `<extract><connection>…` (or equivalent). **Shared-view** filters are siblings under `<shared-view>`. **Worksheet** filters and **slices** live inside `<view>`.

---

## Extract-Level Filters

Defined inside `<extract>` (within the connection). Column references use **no** datasource prefix: `[FieldName]` or `[none:FieldName:nk]`.

Typical pattern: `class='categorical'` with `function='level-members'`, `user:ui-enumeration='all'`, `user:ui-marker='enumerate'` (all members selected by default).

```xml
<filter class='categorical' column='[Product Name (group)]'>
  <groupfilter function='level-members' level='[Product Name (group)]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
<filter class='categorical' column='[none:Category:nk]'>
  <groupfilter function='level-members' level='[none:Category:nk]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
<filter class='categorical' column='[none:Country/Region:nk]'>
  <groupfilter function='level-members' level='[none:Country/Region:nk]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
```

- **column / level:** `[FieldName]` or `[none:FieldName:nk]` (nominal key) in extract context.

---

## Shared-View Filters

Same dimensions as extract-level filters, but the **`column`** attribute uses the **full** instance: `[DatasourceName].[derivation:FieldName:type]`.

Use `context='true'` on filters that should behave as **context filters** across views (not every shared filter requires it; templates may omit `context` on some fields).

```xml
<filter class='categorical' column='[Sample - EU Superstore].[Product Name (group)]'>
  <groupfilter function='level-members' level='[Product Name (group)]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
<filter class='categorical' column='[Sample - EU Superstore].[none:Category:nk]' context='true'>
  <groupfilter function='level-members' level='[none:Category:nk]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
<filter class='categorical' column='[Sample - EU Superstore].[none:Region:nk]' context='true'>
  <groupfilter function='level-members' level='[none:Region:nk]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
```

- **column:** `[DatasourceName].[derivation:FieldName:type]`.
- **context='true':** Marks the filter as a context filter for the workbook (Tableau evaluates context filters before other dimension filters in the pipeline).

---

## Categorical Filters

### `level-members` (all values)

Worksheet-scoped example:

```xml
<filter class='categorical' column='[Sample - EU Superstore].[none:Sub-Category:nk]'>
  <groupfilter function='level-members' level='[none:Sub-Category:nk]' user:ui-enumeration='all' user:ui-marker='enumerate' />
</filter>
```

### Single member (`function='member'`)

String members use XML-escaped quotes: **`&quot;`** around the value.

```xml
<filter class='categorical' column='[Sample - EU Superstore].[:Measure Names]'>
  <groupfilter function='member' level='[:Measure Names]' member='&quot;[Sample - EU Superstore].[sum:Start/End Selected Period Sales (copy)_319755617011306498:qk]&quot;' user:op='manual' />
</filter>
```

Datasource / connection-level single member (e.g. country):

```xml
<filter class='categorical' column='[Country/Region]' filter-group='2'>
  <groupfilter function='member' level='[Country/Region]' member='&quot;United States&quot;'
               user:ui-domain='database' user:ui-enumeration='inclusive' user:ui-marker='enumerate' />
</filter>
```

Worksheet calc filter with “show all” / filter card (`member='true'`):

```xml
<filter class='categorical' column='[Sample - Superstore].[none:Calculation_220113477174652930:nk]'>
  <groupfilter function='member' level='[none:Calculation_220113477174652930:nk]' member='true'
               user:ui-domain='database' user:ui-enumeration='inclusive' user:ui-marker='enumerate' />
</filter>
```

- **groupfilter:** `function='member'` for a single member; `user:ui-domain='database'`, `user:ui-enumeration='inclusive'`, `user:ui-marker='enumerate'` for list-style filters in Superstore-style patterns.
- **filter-group:** Optional; groups filters (e.g. for Apply actions).

### Multi-select / union

Use nested `groupfilter` patterns with `function='union'` when multiple members are selected (Tableau Desktop emits the exact nesting; match an existing workbook when editing).

### `crossjoin` (actions / multi-field)

```xml
<filter class='categorical' column='[Sample - EU Superstore].[Action (MONTH(Order Date (diff format tooltoip)),MY(Order Date))]'>
  <groupfilter function='crossjoin' user:ui-action-filter='[Action3_CB976B5C7C104182BF04CA4CBB0A5993]' user:ui-enumeration='all' user:ui-marker='enumerate'>
    <groupfilter function='level-members' level='[tmn:Order Date (copy)_197876975731912708:ok]' />
    <groupfilter function='level-members' level='[my:Order Date:ok]' />
  </groupfilter>
</filter>
```

### `except` (`kind='hide'`)

Exclude a value (e.g. empty) so the filter card is hidden for that value:

```xml
<filter class='categorical' column='[Sample - EU Superstore].[usr:Calculation_123567527755993096:nk]' kind='hide'>
  <groupfilter function='except' user:ui-domain='relevant' user:ui-enumeration='exclusive' user:ui-manual-selection='true' user:ui-manual-selection-all-when-empty='true' user:ui-marker='enumerate'>
    <groupfilter function='level-members' level='[usr:Calculation_123567527755993096:nk]' />
    <groupfilter function='member' level='[usr:Calculation_123567527755993096:nk]' member='&quot;&quot;' />
  </groupfilter>
</filter>
```

---

## Quantitative Filters

Non-null restriction on measures:

```xml
<filter class='quantitative' column='[Sample - EU Superstore].[sum:Start/End Selected Period Profit (copy)_1036953846741557258:qk]' included-values='non-null' />
<filter class='quantitative' column='[Sample - EU Superstore].[none:Start/End Selected Period Sales (copy)_319755617011306498:qk]' included-values='non-null' />
```

- **column:** Full aggregated or non-aggregated instance (e.g. `sum:...:qk` or `none:...:qk`).
- **included-values='non-null':** Excludes nulls.

Min/max ranges use `<min>` / `<max>` child elements where applicable (see production workbooks for the exact shape on your Tableau version).

---

## Relative-Date Filters

Use **`class='relative-date'`** on the **continuous** date column instance **`[none:FieldName:qk]`**, not the ordinal year/month instance (`[yr:...:ok]`, etc.).

```xml
<filter class='relative-date'
        column='[sqlproxy.0xloa3o1j494z91a039qy0nm99ru].[none:paid_date:qk]'
        first-period='-2'
        include-future='true'
        include-null='false'
        last-period='0'
        period-type='year' />
```

| Attribute | Example | Notes |
|-----------|---------|--------|
| `column` | `[ds].[none:paid_date:qk]` | Continuous date (`:qk`), not ordinal (`:ok`). |
| `period-type` | `'year'` | Use **`period-type`** in generated TWBs. |
| `include-future` | `'true'` | **`'true'`** for filters exposed on the dashboard. |
| `first-period` / `last-period` | e.g. `-2`, `0` | Window relative to anchor. |

**Generated TWBs:** Use **`period-type`**. Tableau Desktop may rewrite to `period-type-v2` on save; see [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md) §13.17 / D2E8DA72 for `period-type-v2` in generated files.

**Dashboard filter zones:** Set **`include-future='true'`** when the relative-date filter appears as a dashboard quick filter.

**Cols/rows conflict:** Do not place a `relative-date` filter on a field that is also on **`<rows>`** or **`<cols>`** — that interaction triggers **A1E47F55**. For trend charts with the date on the axis, restrict the range via the **dashboard filter zone** (slices + zone) instead of a worksheet-level relative-date filter on that field. See [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md) (A1E47F55).

---

## Context Filters

- **Shared-view:** `context='true'` on `<filter>` (see [Shared-View Filters](#shared-view-filters)).
- **LOD interaction:** FIXED LOD expressions are computed before ordinary dimension filters unless those filters are context filters or calcs use `scope-isolation='false'`. Promote filters to context when FIXED must respect them — see [calculated-fields-and-lod.md](calculated-fields-and-lod.md).

---

## Top-N Filters

Do **not** use `class='top'`. Use **`class='categorical'`** with nested **`groupfilter function='end'`** (validated pattern in [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §5c).

```xml
<filter class="categorical" column="[ds].[none:country:nk]">
  <groupfilter count="10" end="top" function="end" units="records"
               user:ui-marker="end" user:ui-top-by-field="true">
    <groupfilter direction="DESC" expression="[Calculation_XXX]"
                 function="order" user:ui-marker="order">
      <groupfilter function="level-members" level="[none:country:nk]"
                   user:ui-enumeration="all" user:ui-marker="enumerate" />
    </groupfilter>
  </groupfilter>
</filter>
```

Add matching **`<slices><column>[ds].[none:country:nk]</column></slices>`** so the filter can appear as a quick filter when needed.

---

## Slices (Quick Filters)

Place **inside `<view>`**, **after** all `<filter>` elements, **before** `<aggregation>`. Each `<column>` must match a worksheet filter column reference so the field appears as a quick filter.

### Standard dimension list

```xml
<slices>
  <column>[Sample - EU Superstore].[none:Category:nk]</column>
  <column>[Sample - EU Superstore].[none:City:nk]</column>
  <column>[Sample - EU Superstore].[none:Country/Region:nk]</column>
  <column>[Sample - EU Superstore].[none:Delivery Mode:nk]</column>
  <column>[Sample - EU Superstore].[none:Order ID:nk]</column>
  <column>[Sample - EU Superstore].[none:Product Name:nk]</column>
  <column>[Sample - EU Superstore].[none:Region:nk]</column>
  <column>[Sample - EU Superstore].[none:Segment:nk]</column>
  <column>[Sample - EU Superstore].[none:State/Province:nk]</column>
  <column>[Sample - EU Superstore].[Product Name (group)]</column>
</slices>
```

### Measures and action columns

```xml
<slices>
  <column>[Sample - EU Superstore].[sum:Start/End Selected Period Profit (copy)_1036953846741557258:qk]</column>
</slices>
```

```xml
<slices>
  <column>[Sample - EU Superstore].[:Measure Names]</column>
  <column>[Sample - EU Superstore].[Action (MONTH(Order Date (diff format tooltoip)),MY(Order Date))]</column>
  <column>[Sample - EU Superstore].[Action (MONTH(Order Date),WEEKDAY(Order Date))]</column>
</slices>
```

Superstore-style parameter/calc slices:

```xml
<slices>
  <column>[Sample - Superstore].[none:Calculation_220113477174652930:nk]</column>
  <column>[Sample - Superstore].[none:Calculation_417990383693557784:nk]</column>
</slices>
```

### Slice column types (optional)

In some **Desktop-saved** workbooks, `<column>` under `<slices>` may carry optional attributes encoding quick filter UI mode. Common values include **`normal`** (default) and **`FI`**, **`FO`**, **`FH`**, **`FR`** (filter control variants). **Programmatically generated TWBs** typically use plain `<column>[Datasource].[field]</column>` only; match a Desktop-exported file if you need parity with a specific control type.

---

## Quick-Filter Title Styling

Use **`style-rule element='quick-filter'`** (and optional **`quick-filter-title`**) to rename cards and set typography:

```xml
<style-rule element='quick-filter'>
  <format attr='title' field='[Sample - EU Superstore].[none:Country/Region:nk]' value='Country' />
  <format attr='title' field='[Sample - EU Superstore].[none:Region:nk]' value='Region' />
  <format attr='title' field='[Sample - EU Superstore].[none:Category:nk]' value='Category' />
  <format attr='title' field='[Sample - EU Superstore].[none:Delivery Mode:nk]' value='Delivery Mode' />
  <format attr='title' field='[Sample - EU Superstore].[none:Segment:nk]' value='Segment' />
  <format attr='font-family' value='Tableau Light' />
  <format attr='color' value='#333333' />
  <format attr='font-size' value='11' />
</style-rule>
<style-rule element='quick-filter-title'>
  <format attr='font-weight' value='bold' />
</style-rule>
```

---

## Dashboard Filter Zones

In the dashboard **`<zones>`** tree (e.g. Filters Container / layout-flow), filter cards use **`type-v2='filter'`**. The **`param`** attribute holds the **same** fully qualified field reference as the worksheet filter / slices (e.g. `[ds].[none:country:nk]`).

**Values mode**

- **`values='relevant'`** — Enumerate from the relevant domain (suited to smaller filter lists).
- **`values='database'`** — Query the database for domain values (use for large domains or when performance characteristics require it).

Choose between `relevant` and `database` based on **domain size and performance**; both are valid.

**Categorical example (typical)**

- `param='[ds].[none:country:nk]'`
- `type-v2='filter'`
- `values='relevant'` or `values='database'` per choice above
- `mode='checkdropdown'` (or other mode Tableau emits for that control)

---

## Date Filter on Dashboard

End-to-end pattern for a **date quick filter** in the dashboard Filters Container (continuous date on `[none:FieldName:qk]` everywhere).

### Relative-Date Filter Setup

- Use **`[none:FieldName:qk]`** in the **filter**, **`<slices>`**, and the dashboard zone **`param`**. Do **not** use the ordinal instance (e.g. `[yr:paid_date:ok]`) for filter/slice/zone.
- Use **`period-type`** on relative-date filters in generated TWBs.
- Set **`include-future='true'`** for dashboard-exposed relative-date filters.

```xml
<filter class='relative-date'
        column='[sqlproxy.0xloa3o1j494z91a039qy0nm99ru].[none:paid_date:qk]'
        first-period='-2'
        include-future='true'
        include-null='false'
        last-period='0'
        period-type='year' />
```

```xml
<slices>
  <column>[sqlproxy.0xloa3o1j494z91a039qy0nm99ru].[none:country (order_items_status):nk]</column>
  <column>[sqlproxy.0xloa3o1j494z91a039qy0nm99ru].[none:order_action:nk]</column>
  <column>[sqlproxy.0xloa3o1j494z91a039qy0nm99ru].[none:paid_date:qk]</column>
</slices>
```

### Worksheet Datasource-Dependencies

Each worksheet that participates must declare the base **`column`** and **`column-instance`** for the continuous date:

```xml
<column aggregation='Year' caption='Paid Date' datatype='date' default-type='ordinal' layered='true'
        name='[paid_date]' pivot='key' role='dimension' type='ordinal' user-datatype='date' visual-totals='Default' />
<column-instance column='[paid_date]' derivation='None' name='[none:paid_date:qk]' pivot='key' type='quantitative' />
```

### Dashboard Filter Zone

- **`param`** = `[ds].[none:FieldName:qk]`
- **`type-v2='filter'`**
- **`values='database'`** for date filters in this pattern
- **No `mode`** attribute (unlike typical categorical zones that use e.g. `mode='checkdropdown'`)

```xml
<zone h='4250' id='252' name='Key Metrics'
      param='[sqlproxy.0xloa3o1j494z91a039qy0nm99ru].[none:paid_date:qk]'
      type-v2='filter' values='database' w='12414' x='0' y='18919'>
  <zone-style>
    <format attr='border-color' value='#000000' />
    <format attr='border-style' value='none' />
    <format attr='border-width' value='0' />
    <format attr='margin' value='4' />
  </zone-style>
</zone>
```

| Attribute | Categorical (e.g. Country) | Date (e.g. Paid Date) |
|-----------|----------------------------|-------------------------|
| `param` | `[ds].[none:country:nk]` | `[ds].[none:paid_date:qk]` |
| `mode` | e.g. `checkdropdown` | *(omit)* |
| `values` | `relevant` or `database` | `database` (this pattern) |

**Dashboard datasource-dependencies** must also include the same **`column`** and **`[none:FieldName:qk]`** `column-instance` so the zone resolves.

### Phone Layout

Replicate the **same** filter zone (same `id`, `param`, `type-v2`, `values`, no `mode`) in the dashboard **Phone** `devicelayout` so the date filter appears on small screens.

### Checklist

1. **Worksheets:** Relative-date filter on `[ds].[none:FieldName:qk]` with `period-type='…'` and `include-future='true'`. **Only** on worksheets where that date is **not** on `<rows>`/`<cols>` if that would trigger A1E47F55; otherwise use dashboard-only filtering for that field.
2. **Worksheets:** Add `[ds].[none:FieldName:qk]` to `<slices>` on each sheet that should respond.
3. **Worksheets:** Datasource-dependencies include `[FieldName]` column and `[none:FieldName:qk]` instance.
4. **Dashboard:** Datasource-dependencies include the same column + instance.
5. **Dashboard:** Filter zone with `param`, `type-v2='filter'`, `values='database'`, no `mode`.
6. **Dashboard:** Copy filter zone to Phone layout when Phone layout exists.

---

## Parameter-Driven Date Filter

For **preset ranges** (This month, Last month, Last 3 months, This year, Last 30 days, **Custom**) plus optional **Start Date** / **End Date** parameters, use a **CASE-based boolean** calculated field and apply it as a **categorical filter** + **slices** on chart worksheets. Full XML and formula patterns: [programmatic-twb-learnings.md §15.12](programmatic-twb-learnings.md) (**Parameter-driven date filter — CASE statement with multiple range options**).

Highlights:

- **Parameters datasource** (`hasconnection='false'`): list parameter for preset selection; **range** parameters for Custom (`min`/`max` only on `<range>` — do not add `granularity` on date range parameters; see D2E8DA72 in [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md)).
- **Boolean “Date Filter” calc** — each `WHEN` branch returns whether a row falls in the chosen range; `Custom` uses `[Parameters].[Start Date]` and `[Parameters].[End Date]`.
- **Apply** like other boolean filters: categorical filter for `true` + `<slices>` entry ([programmatic-twb-learnings.md](programmatic-twb-learnings.md) §13.20 pattern referenced from §15.12).
- Reuse the same CASE logic per datasource, swapping the date field (e.g. `[run_date]` vs `[date_action]`).

---

## Parameters (from Superstore KPI Overview)

Parameters live in a **Parameters** datasource with `hasconnection='false'`. Each parameter is a **column** with:

- **caption** — Display name (e.g. `P. Year`, `P. Metric`, `P. Time Toggle`, `P. Region`, `P. Month`).
- **default-value-field** — Optional; links to a calculated default.
- **param-domain-type** — `'list'` (members) or `'range'` (min/max).
- **value** — Default value.
- **members** — For list parameters: `<member value='...' />` or `<member alias='...' value='...' />`.
- **range** — For range parameters: `<range max='...' min='...' />`.
- **aliases** — Optional: `<alias key='...' value='...' />` for display labels.

Use these patterns when adding dropdowns or range controls to a workbook.

---

## Valid Format Attributes for Filters

Restrict **`format attr`** on **style-rule** elements to attributes known to load cleanly. Unknown attrs (e.g. on wrong elements) can cause **D2E8DA72** — see [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md). The following mirror **Superstore KPI Overview**-valid sets.

### Axis (`element='axis'`)

| attr | Notes |
|------|--------|
| `display` | `class='0'`, `field='...'`, `scope='rows'` or `scope='cols'`, `value='false'` — hide axis |
| `stroke-size` | e.g. `value='0'` |
| `line-visibility` | `value='off'` |
| `tick-color` | e.g. `value='#00000000'` |
| `title` | `field='...'`, `value='Axis Title'` |

```xml
<style-rule element='axis'>
  <format attr='display' class='0' field='[Sample - Superstore].[Latitude (generated)]' scope='rows' value='false' />
  <format attr='display' class='0' field='[Sample - Superstore].[Longitude (generated)]' scope='cols' value='false' />
  <format attr='stroke-size' value='0' />
  <format attr='line-visibility' value='off' />
  <format attr='tick-color' value='#00000000' />
</style-rule>
```

### Cell (`element='cell'`)

| attr | Example |
|------|---------|
| `text-format` | `value='iLLLLL'`, percentages, number formats |
| `vertical-align` | `top` / `center` / `bottom` |
| `text-align` | `left` / `center` / `right` |

### Header (`element='header'`)

| attr | Example |
|------|---------|
| `border-width` | `data-class='total'`, `value='0'` |
| `border-style` | `data-class='total'`, `value='none'` |

### Label (`element='label'`)

| attr | Example |
|------|---------|
| `text-format` | `field='...'`, `value='iLLLLL'` |

### Mark (`element='mark'`)

| attr | Example |
|------|---------|
| `mark-labels-show` | `true` / `false` |
| `mark-labels-cull` | `true` / `false` |
| `mark-labels-mode` | `range` / `line-ends` |
| `mark-labels-range-field` | field ref |
| `mark-labels-range-max` | `false` |
| `mark-color` | hex |
| `mark-line-pattern` | `solid` / `dashed` |
| `mark-transparency` | 0–255 |
| `size` | numeric |
| `shape` | e.g. custom shape path |

### Pane (`element='pane'`)

| attr | Example |
|------|---------|
| `border-width` | `data-class='total'` |
| `border-style` | `data-class='total'` |

### Table (`element='table'`)

| attr | Example |
|------|---------|
| `show-null-value-warning` | `false` |
| `background-color` | e.g. transparent hex |

### Gridline, zeroline, dropline, refline

| element | Typical attrs |
|---------|----------------|
| `gridline` | `stroke-size` 0, `line-visibility` off |
| `zeroline` | `line-pattern-only`, `stroke-size`, `line-visibility` |
| `dropline` | `stroke-size`, `line-visibility` |
| `refline` | `line-pattern-only`, `stroke-size`, `line-visibility` |

### Table-div (`element='table-div'`)

| attr | Example |
|------|---------|
| `stroke-size` | `scope='cols'`, `value='0'` |

### Map (`element='map'`)

| attr | Example |
|------|---------|
| `washout` | `value='0'` |

---

## Anti-Patterns

Attributes that are **not** in the safe enumerations for generated loads (examples from Superstore KPI guidance):

- **`attr='alignment'`** under `element='worksheet'` — not in enumeration; set alignment in Tableau Desktop if needed.
- **`attr='default-format'`** under `element='axis'` — not in enumeration; set number format on the field or in Desktop.

For **invalid `format attr` names** and schema validation failures, see **D2E8DA72** in [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md) (including §24.13).

---

## Summary Table

| Location | Column format | groupfilter / attribute | Notes |
|----------|---------------|---------------------------|--------|
| `<extract>` | `[Field]` or `[none:Field:nk]` | `function='level-members'`, `user:ui-enumeration='all'` | No datasource prefix |
| `<shared-view>` | `[DS].[…]` | Same; often `context='true'` | Workbook-level shared filters |
| `<view>` categorical | `[DS].[…]` | `level-members` \| `member` \| `crossjoin` \| `except` | Worksheet-level |
| `<view>` quantitative | `[DS].[agg:calc:qk]` etc. | `included-values='non-null'` | Drop nulls |
| Top-N | `[DS].[…]` | `function='end'` on nested `groupfilter` | Not `class='top'` |
| Relative-date | `[DS].[none:Field:qk]` | `period-type`, `include-future='true'` | Not on same field as rows/cols when it triggers A1E47F55 |
| `<slices>` | Same as filter column | N/A | Quick filter cards; before `<aggregation>` |
| Dashboard filter zone | Same field ref as slices | `type-v2='filter'`, `values` per domain | Date: often `values='database'`, no `mode` |

Use these patterns when authoring or editing `.twb` / `.twbx` so filter XML stays consistent with validated templates and programmatic rules.
