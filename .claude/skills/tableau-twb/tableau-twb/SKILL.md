---
name: tableau-twb
description: Create, read, and modify Tableau workbook (.twb) and data source (.tds) XML files, and interact with Tableau Server/Cloud via REST API. Use when working with Tableau visualizations programmatically including creating dashboards, worksheets, charts (bar, line, scatter, pie, area, map), connecting to data sources (Excel, databases, Databricks, published datasources, direct/federated connections, Custom SQL), defining calculated fields, parameters, filters, dashboard layouts, publishing workbooks to Tableau Server/Cloud, managing permissions, and automating extract refreshes. Handles TWB/TWBX workbook formats, TDS/TDSX data source files, Tableau REST API (tsRequest/tsResponse XML), sqlproxy connections to published datasources, and federated direct connections to Databricks and other databases.
---

# Tableau TWB XML & REST API Skill

Create and manipulate Tableau workbook files (.twb/.twbx) and data sources (.tds/.tdsx) programmatically via XML. Publish and manage content on Tableau Server/Cloud via REST API. **Supports both published data source connections (`sqlproxy`) and direct database connections (`federated`)** for production Tableau workbooks.

## Two Data Connection Patterns

### Pattern 1: Published Data Source (`sqlproxy`) — Governed

When connecting to a **published data source** on Tableau Cloud/Server, use the `sqlproxy` connection class:

```xml
<datasource caption='My Data (Published)' name='sqlproxy.1rfw7xb1xv29kt1cv7fne0cre0xx' inline='true' version='18.1'>
  <repository-location derived-from='http://server.com/t/site/datasources/MyPublishedDataSource?rev=1.2' 
                       id='MyPublishedDataSource' path='/t/site/datasources' 
                       revision='1.3' site='MySiteName' />
  <connection channel='https' class='sqlproxy' dbname='MyPublishedDataSource' 
              directory='/dataserver' local-dataserver='' port='443' 
              server='your-pod.online.tableau.com' 
              server-ds-friendly-name='My Data (Published)' 
              username='' workgroup-auth-mode='prompt'>
    <relation type='collection'>
      <relation name='sqlproxy' table='[sqlproxy]' type='table' />
    </relation>
  </connection>
</datasource>
```

See **[references/connections-and-datasources.md](references/connections-and-datasources.md)** for complete examples.

### Pattern 2: Direct Database Connection (`federated`) — Flexible

When connecting **directly to a database** (Databricks, SQL Server, etc.) without a published data source, use the `federated` connection wrapper with a `named-connection` containing the actual database connector. Supports Custom SQL and direct table references:

```xml
<datasource caption='My Query' name='federated.02bm58x14zgdy9188vvi70n3vz3a' inline='true' version='18.1'>
  <connection class='federated'>
    <named-connections>
      <named-connection caption='dbc-XXXX.cloud.databricks.com' name='databricks.0fy96ry16x2arq100fydu0fmm2qe'>
        <connection authentication='auth-pass' class='databricks'
                    dbname='your-catalog' schema='marts'
                    server='dbc-XXXX.cloud.databricks.com'
                    v-http-path='/sql/1.0/warehouses/WAREHOUSE_ID'
                    workgroup-auth-mode='prompt'>
          <connection-customization class='databricks' enabled='false' version='18.1'>
            <vendor name='databricks' /><driver name='databricks' />
            <customizations><!-- capability flags --></customizations>
          </connection-customization>
        </connection>
      </named-connection>
    </named-connections>
    <relation connection='databricks.0fy96ry16x2arq100fydu0fmm2qe'
             name='Custom SQL Query' type='text'>SELECT * FROM `catalog`.`schema`.`table`</relation>
    <metadata-records><!-- column type mappings --></metadata-records>
  </connection>
</datasource>
```

See **[references/connections-and-datasources.md](references/connections-and-datasources.md)** for complete examples with Custom SQL, metadata-records, Python generation, and capability flags.

### When to Use Which

| Aspect | Published (`sqlproxy`) | Direct (`federated`) |
|--------|------------------------|----------------------|
| Custom SQL in workbook | No | **Yes** |
| Centralized governance | **Yes** | No |
| Requires Tableau Server | **Yes** | No |
| Best for | Production dashboards | Ad-hoc queries, prototypes, Custom SQL |

A single workbook can **mix both patterns** (e.g., Management Dashboard uses `sqlproxy` for Revenue view + `federated` for Custom SQL queries).

## File Types

| Extension | Description | Contains Data? |
|-----------|-------------|----------------|
| .twb | Workbook XML | No - references data sources |
| .twbx | Packaged workbook (zip) | Yes - includes extracts/images |
| .tds | Data source XML | No - connection metadata only |
| .tdsx | Packaged data source | Yes - includes extract |

**TWBX/TDSX files**: Rename to `.zip` to extract contents, including the `.twb`/`.tds` XML file.

## Workflow: Create Workbook → Connect to Published DS → Publish

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ 1. Get DS Metadata  │ ──► │ 2. Generate TWB     │ ──► │ 3. Publish Workbook │
│    (REST API)       │     │    (XML with        │     │    (REST API)       │
│                     │     │     sqlproxy conn)  │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Step 1: Get Published Data Source Info

**Option A: Using Tableau MCP (Recommended)**
```python
# Use MCP tools to automatically fetch data source information
# - list-datasources: List all published data sources
# - get-datasource-metadata: Get column information
# - search-content: Search for data sources by name
```

**Option B: Using REST API**
```python
import tableauserverclient as TSC
auth = TSC.PersonalAccessTokenAuth('pat-name', 'pat-secret', 'site')
server = TSC.Server('https://your-cloud.online.tableau.com', use_server_version=True)
with server.auth.sign_in(auth):
    datasources, _ = server.datasources.get()
    for ds in datasources:
        print(f"Name: {ds.name}, ID: {ds.id}, Content URL: {ds.content_url}")
```

### Step 2: Generate TWB with sqlproxy Connection
Use [scripts/generate_twb.py](scripts/generate_twb.py) or build XML directly (see examples below).

### Step 3: Publish to Tableau Cloud/Server
```python
with server.auth.sign_in(auth):
    wb_item = TSC.WorkbookItem(project_id='proj-id')
    server.workbooks.publish(wb_item, 'my_workbook.twb', 
                             mode=TSC.Server.PublishMode.Overwrite,
                             skip_connection_check=True)  # Important!
```

## Official Python Libraries

| Library | Purpose | Install |
|---------|---------|---------|
| `tableauserverclient` | REST API client | `pip install tableauserverclient` |
| `tableaudocumentapi` | Modify TWB/TDS (unsupported) | `pip install tableaudocumentapi` |
| `tableauhyperapi` | Create .hyper extracts | `pip install tableauhyperapi` |
| `langchain-tableau` | AI/LangChain integration | `pip install langchain-tableau` |

**Note**: `tableaudocumentapi` does NOT support creating files from scratch - use direct XML generation.

## Alternative Workflow

1. **Read existing TWB** → Parse XML with Python `xml.etree.ElementTree`
2. **Create new TWB** → Build XML structure following schema below
3. **Modify TWB** → Edit elements, save with UTF-8 encoding
4. **Validate** → Run `validate_twb()` (XSD + structural checks) — must output `Validation PASSED` before delivery

## Critical: Two XML Schemas

Tableau uses **two separate XML schemas** — do not mix them:

| Schema | Purpose | Use when |
|--------|---------|----------|
| **TWB Workbook XML** | Internal .twb structure (workbooks, dashboards, parameters, filters) | Generating or editing .twb files |
| **REST API XML** | `tsRequest`/`tsResponse` for Server/Cloud API | Publishing, downloading, managing content |

This skill and the references below focus on **TWB Workbook XML**. For REST API, see [references/rest-api.md](references/rest-api.md).

## Core XML Structure

See **[references/xml-schema-and-structure.md](references/xml-schema-and-structure.md)** for the full TWB schema (parameters, filters, dashboard containers, worksheets, datasources, actions, minimal template, generation best practices, and element reference).

```xml
<?xml version='1.0' encoding='utf-8' ?>
<workbook source-build='2025.3.3 (20253.26.0206.0336)' source-platform='mac' version='18.1' 
          xmlns:user='http://www.tableausoftware.com/xml/user'>
  <document-format-change-manifest>
    <WindowsPersistSimpleIdentifiers />
    <_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners />
    <!-- ... -->
  </document-format-change-manifest>
  <preferences/>
  <datasources>
    <!-- Only include <datasource name='Parameters'/> if the workbook has parameters -->
    <datasource name='MyData' inline='true'/>
  </datasources>
  <worksheets>
    <worksheet name='Sheet1'/>
  </worksheets>
  <dashboards>
    <dashboard name='Dashboard1'/>
  </dashboards>
  <windows>
    <window class='dashboard' name='Dashboard1' />
  </windows>
</workbook>
```

## Quick Reference

### Mark Types (Visualization Types)
`<mark class='X'/>` where X is: `Automatic`, `Bar`, `Line`, `Area`, `Square`, `Circle`, `Shape`, `Text`, `Map`, `Pie`, `Gantt`, `Polygon`, `Density`

### Shape Marks and KPI Trend Indicators
- **Shape encoding XML:** `<shape column='[ds].[none:FieldName:nk]'/>` inside `<encodings>`
- **Shape mapping:** `<encoding attr='shape' field='...' type='shape'>` with `<map to='PaletteName/filename.png'><bucket>"Value"</bucket></map>` in `<style-rule element='mark'>`
- **Built-in shapes:** `circle`, `square`, `triangle`, `diamond`, `cross`, `plus`, `filled-circle`, `filled-square`, `filled-triangle`
- **Custom shapes:** Referenced as `PaletteFolderName/filename.ext`; all files in folder are Base64-embedded in TWB — isolate only needed shapes
- **Always dual-encode:** Place trend field on BOTH Shape and Color shelves (WCAG 1.4.1 — never color-only or shape-only)
- **Zero-calc alternative:** Custom number format `▲+0.0%;▼-0.0%;0.0%` renders arrows inline without calculated fields or shape marks
- **Dual-axis overlay:** Two `<pane>` elements — pane 1 = Bar/Line, pane 2 = Shape with independent `<mark>` and `<encodings>`
- **Custom shape images:** PNG with transparent background mandatory for color encoding (JPG produces colored rectangles); 32×32 px, under 50 KB
- Full reference: **[references/kpi-cards-and-trends.md](references/kpi-cards-and-trends.md)**

### Field Types
- `type='quantitative'` → Continuous measure
- `type='nominal'` → Discrete dimension (string)
- `type='ordinal'` → Discrete dimension (numeric)

### Field Roles
- `role='dimension'` → Qualitative grouping
- `role='measure'` → Quantitative aggregation

### Common Data Types
`datatype='string'`, `'integer'`, `'real'`, `'date'`, `'datetime'`, `'boolean'`

### Connection Classes
- **Direct DB:** `databricks`, `sqlserver`, `postgres`, `mysql`, `redshift`, `snowflake`, `bigquery`, `excel-direct`, `hyper`
- **Published DS:** `sqlproxy` (Tableau Server/Cloud)
- **Wrapper:** `federated` (wraps direct DB connectors with named-connections)

### Zone visibility: Show/Hide buttons and Dynamic Zone Visibility
- **Show/Hide buttons (2019.2+):** **WARNING: `<button>` / `<toggle-action>` is NOT valid in programmatically generated TWBs** (D2E8DA72: "no declaration found for element 'button'"). Use DZV datagraph + paramctrl instead (§15.10). The toggle-button pattern works only in Tableau Desktop-saved files. For reference: In Tableau 2025.3, the button zone is a sibling of root under `<zones>`, `type-v2='dashboard-object'` with `<toggle-action>` inside `<button>`. See [references/dashboard-layout-and-zones.md](references/dashboard-layout-and-zones.md) for the XML structure.
- **Info buttons:** Use toggle buttons with `icons8-info-96.png` icons to show/hide documentation panels. Each dashboard should have its own info button explaining KPI definitions and usage. Pattern: `<button action='' active-visual-state-index='1'>` with two `<button-visual-state>` (empty + icon image). Info panel: `hidden-by-user='true'`, white bg, 1px gray border, 30px padding.
- **Container names:** Use `friendly-name='...'` on layout zones (e.g. `Filters Container`, `Dashboard Information`, `Viz Column`) so they appear in the Item Hierarchy and when configuring show/hide targets.
- **Dynamic Zone Visibility (2022.3+):** Uses a **datagraph node system** (NOT zone-level attributes). The `<datagraph>` contains `dashboard-zone-visibility-node` (bound to a zone via `zone-id`) and `single-value-field-node` (boolean calc field via `fieldname`) connected by `<edge>` elements. Target zones use `hidden-by-user='true'` as default state. Required manifest entries: `ZoneVisibilityControl`, `DatagraphNodeDashboardZoneVisibilityV1`, `DatagraphNodeSingleValueFieldV1`. Use `uuid.uuid4()` for all GUIDs when generating programmatically.
- **DZV + Parameter Actions pattern (recommended for KPI drilldowns):** Worksheet button zones fire `edit-parameter-action` to set an Open/Close string parameter. A boolean calc (`[Parameters].[Open Close] = 'Open'`) feeds the datagraph. Each KPI button also sets a "Measure Name" parameter to drive drilldown content. A Close button resets to "Close". See [references/dashboard-layout-and-zones.md](references/dashboard-layout-and-zones.md) for complete XML.
Full structures, zone types, datagraph pattern, and info button pattern: [references/dashboard-layout-and-zones.md](references/dashboard-layout-and-zones.md).

### Folder Organization (Calculated Fields)
Group calculated fields into logical folders using `<folders-common>` inside `<datasource>`, placed after all `<column>` elements and before `<layout>`. Each `<folder name='...'>` contains `<folder-item name='[field_name]' type='field' />` entries. Set `<layout show-structure='true' />` to display folders in the Data pane. Recommended folder naming: `"Sales: CY vs PY"`, `"Dynamic Category"`, `"Display View"`, etc. See §6.1 in [references/xml-schema-and-structure.md](references/xml-schema-and-structure.md).

### Generation Best Practices (TWB)
When generating .twb XML: use `&quot;` for all string values in parameters and filters; include `<datasource-dependencies>` for every field used in views; use unique integer zone IDs; root dashboard zone must be `x='0' y='0' w='100000' h='100000'`; include `<windows>` with the active sheet. Full DO/DON'T and validation: [references/xml-schema-and-structure.md](references/xml-schema-and-structure.md).

### Critical Structural Rules (TWB generation)
These rules prevent the most common load errors (**D2E8DA72**, **2805CF18**, **A1E47F55**). Full details in [references/programmatic-twb-learnings.md](references/programmatic-twb-learnings.md) §13.

- **Window structure (§13.1):** Never use empty `<cards />` or `<viewpoints />` in `<window>` elements. Dashboard windows must list all worksheets in `<viewpoints>`. Worksheet windows must include the full `<cards>` structure (edges, strips, card types) and `<viewpoint>` with zoom. Empty children cause **Error Code: 2805CF18**.
- **Table element ordering (§13.2):** Inside `<table>`: `<view>` → `<style>` → `<panes>` → `<rows>` → `<cols>`. Rows/cols are direct children of `<table>`, never inside `<view>`. `<aggregation value="true" />` must be inside `<view>`.
- **Date column types (§13.3):** In `<datasource-dependencies>`, date `<column>` uses `type="ordinal"`, date `<column-instance>` uses `type="quantitative"` for continuous axis.
- **Manifest entries (§13.7):** Only include `ObjectModelEncapsulateLegacy`. Do not include `enable-sort-zone-taborder` (causes D2E8DA72).
- **`simple-id` (§13.6):** Do not add `<simple-id>` to `<window>` elements. Tableau adds it on save.
- **`source-build` (§13.5):** Required attribute on `<workbook>` root element.
- **Minimal strategy (§13.10):** Omit `metadata-records`, `folders-common`, `semantic-values`. Use minimal column definitions in deps. Populate all structural elements. Let Tableau Desktop fix up on first open.
- **Custom SQL `<` characters (§14.1):** Tableau's Custom SQL parser treats ALL `<` as parameter markers (`<ParameterName>`). Reverse every `<` and `<=` comparison to `>` / `>=` (e.g., `a < b` → `b > a`). CDATA wrapping does NOT prevent this. Wrap SQL in CDATA for other special chars.
- **No `group-label-config` in 2025.3 (§14.3):** `group-label-config` is NOT allowed inside `customized-label`. Use `formatted-text` as direct child.
- **No `<mark>` in `style-rule` in 2025.3 (§14.4):** `<mark class='...'>` is NOT allowed inside `<style-rule>`. Place mark type only in `<pane>`.
- **BAN field references (§14.5):** Label field references use `<![CDATA[<[datasource].[field]>]]>` in `<run>` text — NOT `AGG([field])` as plain text.
- **BAN line breaks (§14.6):** Use `Æ&#10;` in label runs, not `\n`.
- **No empty `Parameters` datasource (§14.7):** Omit `<datasource name="Parameters">` when the workbook has no parameters.
- **Relative-date filter vs axis conflict (§13.16):** NEVER put a `relative-date` filter on a field that is also on the `<cols>` or `<rows>` shelf — causes **A1E47F55**. Use dashboard-level filter zones instead for date range filtering on trend charts.
- **`luid` NOT valid on `repository-location` (§15.2):** Do NOT add `luid="..."` to `<repository-location>`. It causes D2E8DA72. Use `contentUrl` for `id` and `dbname`.
- **Dimension calc derivation (§15.3):** Calculated fields with `role="dimension"` (no aggregation — DATETRUNC, CASE switchers) must use `derivation="None"` / `none:` prefix. Using `usr:` causes AGG on shelf. Measure calcs (with SUM etc.) use `derivation="User"` / `usr:`. Arrow calcs are measures (`usr:`), not dimensions. Note: `DATETRUNC()` returns `datetime` — use `datatype="datetime"` even when the source field is `date`.
- **List parameter: members only (§15.4):** `param-domain-type="list"` uses `<members>` ONLY — `<range>` is mutually exclusive. Both together causes D2E8DA72.
- **Measure Names / Measure Values (§15.6):** These are **implicit built-in fields** — do NOT define them in `<datasource-dependencies>`. Reference as `[ds].[:Measure Names]` and `[ds].[Multiple Values]`. Do NOT use derivation prefixes (`none::Measure Names:nk` is WRONG). Filter on `[:Measure Names]` with `level="[:Measure Names]"` and `member` = fully-qualified column-instance ref. For dual-axis with total: rows = `([ds].[Multiple Values] + [ds].[usr:total:qk])` — parentheses and `+` are REQUIRED (space-separated causes "Malformed expression"). Three panes with `y-axis-name` on panes 1 and 2. See §15.6 for text-table, dual-axis, and axis styling patterns.
- **Measure Names color encoding (§15.6b):** To assign colors to `[:Measure Names]` programmatically, add color encoding at the **datasource level** (not worksheet). Three prerequisites: (1) `<column-instance>` elements at the datasource level for every measure in the color legend, (2) `<layout show-structure='true' />` at the datasource level, (3) bucket values in `"[ds_name].[derivation:col:suffix]"` format (fully-qualified with escaped quotes). Place encoding inside `<style><style-rule element='mark'><encoding attr='color' field='[:Measure Names]' type='palette'>`. Worksheet-level encoding, `palette` attribute on `<color>`, and bucket values without datasource prefix or quotes all fail. See §15.6b for complete XML pattern.
- **Legend subtitle for multi-measure charts (§15.9):** Every chart with multiple measures (colored by `[:Measure Names]`) MUST include a colored-square legend subtitle in the worksheet title. Place it inside `<layout-options><title><formatted-text>`. Pattern: title run → `Æ&#10;` line break → for each measure: colored `■` run + caption run. Use `fontsize='9'` for legend items. Separate items with three trailing spaces. The `■` run uses `fontcolor` matching the measure's assigned color; the caption run uses `fontcolor='#525252'`. XML:
  ```xml
  <layout-options><title><formatted-text>
    <run fontcolor='#525252' fontname='Tableau Medium' fontsize='11'>Chart Title</run>
    <run>Æ&#10;</run>
    <run fontcolor='#7380AB' fontsize='9'>■ </run>
    <run fontcolor='#525252' fontsize='9'>Measure One   </run>
    <run fontcolor='#3296ED' fontsize='9'>■ </run>
    <run fontcolor='#525252' fontsize='9'>Measure Two</run>
  </formatted-text></title></layout-options>
  ```
- **Generated-TWB-only pitfalls (§15.7):** `<manual-sort>` causes D2E8DA72 (not in schema); `mark-line-pattern` format attr causes D2E8DA72 ("value not in enumeration"); `[Multiple Values]` alone on rows/cols causes "Malformed expression" — only works in `(A + B)` dual-axis or `<text>` encodings; `<button>` / `<toggle-action>` is NOT valid ("no declaration found for element 'button'") — use DZV datagraph + paramctrl instead (§15.10); `derivation` attribute on `<column>` is NOT valid — only use on `<column-instance>`; `<datagraph>` inside `<dashboard>` is NOT valid — must be workbook-level after `<windows>`. These elements work in Tableau-saved files but are rejected on initial load of generated TWBs.
- **DZV programmatic implementation (§15.10):** For DZV in generated TWBs: (1) Add a Show/Hide string parameter + boolean calc (`[Parameters].[Show X] = 'Show'`); (2) Use `type-v2='paramctrl'` zone in dashboard for the dropdown; (3) Make the DZV panel a **floating sibling of root `layout-basic` zone** (direct child of `<zones>`, with absolute x/y/w/h coords); (4) Set `hidden-by-user='true'` on the panel root AND every child zone; (5) Add `<datagraph>` as a **workbook-level** element after `<windows>` with `single-value-field-node` → `dashboard-zone-visibility-node` for each hidden zone; (6) Add manifest entries: `DatagraphCoreV1`, `DatagraphNodeDashboardZoneVisibilityV1`, `DatagraphNodeSingleValueFieldV1`, `ZoneVisibilityControl`. Do NOT use `<button>`/`<toggle-action>` — it fails in generated TWBs. See §15.10 for complete XML and Python patterns.
- **Zone styling — margin/padding (§15.8):** Apply `margin` (outer padding) and `padding` (inner padding) **directly on the worksheet zone**, NOT on a wrapping `layout-flow` container. Tableau ignores margin/padding on container zones. Put worksheet zones directly inside row/column zones.
- **Paramctrl mode and styling (§15.11):** Use `mode='compact'` for string list params (dropdown) and `mode='datetime'` for date params (date picker). Add `background-color` matching canvas bg (`#f0f3fa`), `border-style='none'`, `margin='4'`, `padding='2'`. Distribute widths equally (e.g. 5 controls at `w='20000'`). Place all paramctrls in a horizontal Filters Row (`fixed-size='32'`) between title and KPI rows.
- **Parameter-driven date filter (§15.12):** Use a CASE-based boolean calc driven by a "Date Parameter" list parameter with presets (This month, Last month, Last 3 months, This year, Last 30 days, Custom). "Custom" uses Start Date / End Date range parameters. Apply as categorical filter + slices on all chart worksheets. **CRITICAL:** Do NOT use `granularity` attribute on `<range>` for date parameters — `granularity='day'` causes error "value 'day' neither 'false' nor 'true'". Only `max` and `min` are valid.
- **`period-type` and `include-future='true'` (§13.17):** Use `period-type` (not `period-type-v2`) on `<filter class="relative-date">` when generating TWB files — `period-type-v2` causes D2E8DA72. Tableau Desktop converts to `period-type-v2` internally on save. Always set `include-future='true'` — using `'false'` causes **A1E47F55** when the filter is exposed on a dashboard.
- **No dashboard-level deps (§13.18):** Do not add `<datasources>` or `<datasource-dependencies>` as direct children of `<dashboard>` in generated TWBs — causes **A1E47F55**. Filter zones resolve fields through their `name` (worksheet reference).
- **Month display (§13.19):** Use `[tmn:FieldName:qk]` with `derivation='Month-Trunc'` on the cols shelf for month-level axis. Keep `[none:FieldName:qk]` for filters/slices. Include both instances in worksheet `<datasource-dependencies>`.
- **Date-range filtering on trend charts (§13.20):** When date is on cols, use a boolean calculated field (e.g., `DATEDIFF("month", [date_month], TODAY()) >= 0 AND ... <= 11`) with a categorical filter for `true`, instead of a `relative-date` filter.
- **Default dashboard size:** Use `<size maxheight='900' maxwidth='1300' minheight='900' minwidth='1300' />` (1300x900) for all new desktop dashboards unless the user specifies otherwise.
- **Even layout distribution (§13.21):** Worksheet zones in horizontal containers need equal `w` values and `layout-cache` with `minwidth='100' minheight='130' type-w='scalable' type-h='scalable'`.
- **Hiding field labels (§25.9):** Use `<style-rule element="worksheet"><format attr="display-field-labels" scope="cols" value="false" /><format attr="display-field-labels" scope="rows" value="false" /></style-rule>`. The `element="label"` approach does NOT work. Also add `element="field-labels"` with `attr="display"` for belt-and-suspenders. Both must be present.
- **Hiding measure axis per-field (§25.10):** Add `<format attr="display" class="0" field="[ds].[sum:measure:qk]" scope="cols" value="false" />` inside the `axis` style-rule. Target the specific measure column-instance ref and its shelf scope (cols for horiz bars, rows for vertical/monthly charts). Sparklines hide both axes.
- **Hiding worksheet titles in dashboard (§25.8):** Add `show-title="false"` on the worksheet `<zone>` in the dashboard. Removing the title strip from `<window>` cards does NOT affect dashboard zones.
- **edit-parameter-action name brackets (§25.1):** The `name` attribute must use bracket notation: `name="[Set Sales]"` not `name="Set Sales"`.
- **Parameter string values — no double encoding (§25.4):** Set values as `'"Sales"'` in Python. The XML library handles encoding. Using `'&quot;Sales&quot;'` causes double-encoding.
- **Inline cross-referenced calcs (§25.6):** Calculated fields that reference other calcs by caption may fail to resolve in generated TWBs. Inline all dependent formulas directly.
- **border-radius NOT valid (§25.7):** Use `DashboardRoundedCorners` manifest entry instead of `border-radius` format attr.
- **Excel join expressions use relation name (§25.5):** In join `<expression>` elements, use the relation `name` (e.g., `[Orders]`), not the `table` attribute (e.g., `[Orders$]`).
- **zone-style must be LAST child (§28.1):** In `layout-basic` and `layout-flow` container zones, `<zone-style>` MUST be the last child element — after all child `<zone>` elements. Placing it first causes **D2E8DA72** (`element 'zone' is not allowed for content model`).
- **No multiple measures on a single shelf (§28.2):** Space-separated measures on `<rows>` or `<cols>` (e.g., `[ds].[sum:a:qk] [ds].[sum:b:qk]`) cause "Malformed expression" in generated TWBs. Use the dual-axis pattern with parentheses+plus instead: `([ds].[sum:goal:qk] + [ds].[sum:actual:qk])`. This works for BOTH the same measure twice (sparklines) AND two different measures (grouped bars). See §28.12 for the complete pattern including 3 panes, Measure Names color encoding, synchronized axis, and datasource-level prerequisites.
- **Cross-referenced calcs are implicitly aggregated (§28.3):** Any calculated field whose formula references another calc via `[Calculation_XXXXX]` should use `derivation="User"` / `usr:` prefix, because the referenced calc likely contains aggregation. Extend `has_agg()` to detect `[Calculation_` references.
- **Sparklines must use raw fields, not BAN calcs (§28.4):** BAN `_cy` calcs filter to the current month only (single dot). Sparklines need the full 12-month trend. Use raw source fields for simple sums or dedicated trend calcs for ratios.
- **fit-width zoom for long tables (§28.5):** Worksheets with many rows (campaigns, summaries) should use `<zoom type="fit-width"/>` in both worksheet and dashboard viewpoints.
- **Date fields: use Month-Trunc for date axis (§28.6):** Always use `datatype="date"`, `type="ordinal"`, `derivation="Month-Trunc"` / `tmn:field:qk` for date axes. Discrete `none:field:nk` shows text labels, not a proper date axis.
- **Boolean date-range filters (§28.7):** For fixed date ranges (e.g., `>= 2025`), use a boolean calc with Tableau date literal syntax (`[month] >= #2025-01-01#`) applied as a categorical filter for `true`. More reliable than `relative-date` in generated TWBs.
- **Official XSD schema (§25.15):** Vendored at `schemas/twb_2026.1.0.xsd`. Every generator MUST call `validate_twb()` at the end of `generate()` — the function runs XSD validation (advisory, Tier 1) and custom structural checks (blocking, Tier 2). The TWB is not delivered until `Validation PASSED` appears.
- **Version 18.1 with individual manifest:** Generated workbooks use `version="18.1"` with individual manifest entries (NOT `ManifestByVersion`, which requires version 26.1 + additional undocumented elements). Rounded corners use `_.fcp.DashboardRoundedCorners.true...format` elements with post-processing string fixup.
- **KPI cards / BANs default to FULL comparison (§13.22):** The **default** BAN is always a **full KPI card with comparison** (vs Previous Month AND vs Last Year) — never a simple standalone number. Only use a simple BAN (§14.11) when the user explicitly requests no comparisons. Do NOT use a `relative-date` filter. Embed all date filtering in calc field formulas (e.g., `SUM(IF DATEDIFF("month", [date], TODAY()) = 0 THEN [measure] END)`). Each comparison line needs 6 calcs: current value, previous value, positive % change, negative % change, positive arrow, and negative arrow. Use the **split positive/negative technique** for conditional green (`#1ea86c`) / red (`#ca1325`) coloring: separate calculated fields for positive and negative values, each with its own `fontcolor` in the customized-label. When positive, the negative fields are null (hidden) and vice versa. All fields must be in encodings AND customized-label with one field per `<run>` element.

### Calculated fields (definitive guide)

**Primary reference:** [references/calculated-fields-and-lod.md](references/calculated-fields-and-lod.md) — XML generation rules, encoding, parameters, table calcs, LOD, pitfalls.

**Rules to follow:**
- **Where they live:** Definitions (formula) in `<datasource>` after `<aliases enabled='yes' />`; table calc **configuration** (addressing/partitioning) in the worksheet’s `<column-instance>` with `<table-calc>`, not in the datasource.
- **Minimal column pattern (“Test” pattern):** Use only `caption`, `datatype`, `name`, `role`, `type` on the `<column>`; put the formula in `<calculation class='tableau' formula='...' />`. Omit `aggregation`, `pivot`, `layered`, `default-type`, `user-datatype`, `visual-totals` so Tableau treats it as a user-created calculated field.
- **Formula required:** Every calculated field must have a child `<calculation class='tableau' formula='...' />`. A self-closing `<column />` with no formula causes “field doesn’t exist” in Tableau.
- **Worksheet reference:** When a sheet uses a calc defined in the datasource, reference it with a minimal `<column caption='...' datatype='...' name='...' role='...' type='...' />` in that sheet’s `<datasource-dependencies>` — do **not** repeat the formula in the worksheet.
- **XML encoding:** In formula attributes use `&quot;` `&lt;` `&gt;` `&apos;` `&amp;` and `&#10;` for newlines. Use an XML library to set formula values; never concatenate strings manually.
- **Tableau formula syntax is NOT SQL (§14.9):** Use `ISNULL([field])` not `[field] IS NULL`; `IFNULL([a],[b])` not `COALESCE(a,b)`; `ZN([a])` for null-to-zero. Always reference [references/tableau-functions-reference.md](references/tableau-functions-reference.md) for valid syntax. Format multi-line formulas with each clause on its own line.
- **Parameters:** Reference as `[Parameters].[Parameter Name]`. Date range parameters: `<range min='...' max='...' />` only — **do not** add `period` on `<range>` (causes load error D2E8DA72).
- **Table calculations:** Formula (e.g. `LOOKUP(..., -1)`) in datasource `<column>`; `<table-calc ordering-type='Rows' />` can live in the `<calculation>` in the datasource and must be reflected in the worksheet’s `<column-instance>` for compute-using.
- **LOD:** Use `scope-isolation='false'` on `<calculation>` when FIXED LOD or cross-datasource refs should respect data source filters.
- **BAN “% vs previous”:** Reuse an existing calculated field when one exists; reference it in the worksheet and use its column-instance (e.g. `[usr:Calculation_...:qk]`) in encodings and customized-label.
- **Arrow calc derivation:** Arrow fields (datatype string, type nominal) that contain aggregate functions (SUM, COUNTD) **must** use derivation User / `[usr:...:nk]` in column-instance, encodings, and customized-label -- **not** derivation None / `[none:...:nk]`. Using None derivation for aggregate calcs prevents Tableau from evaluating them. This applies to ALL string calcs containing aggregate functions, not just arrows.
- **Aggregate string calcs (§25.11):** Any calculated field returning a string that contains SUM/COUNTD/AVG etc. is an aggregate calc. Even though the datatype is string, the `column-instance` must use `derivation="User"` with `usr:` prefix. Example: `IF SUM([Sales]) > 0 THEN "▲" ELSE "▼" END` → `[usr:Calculation_xxx:nk]`.
- **Customized-label run splitting:** Each field reference in a customized-label must be in its **own** `<run>` element. Never combine two field references in one run (e.g. arrow + percent change). Split them into separate runs.
- **Percentage default-format:** Ratio calculated fields (e.g. % change) display as raw decimals (0.058) unless you add `default-format='p0.0%'` to the `<column>` element. This must be set on **every** occurrence -- both the main datasource column and each worksheet's datasource-dependencies copy.
- **Currency default-format:** Dollar amount fields use `default-format='c&quot;$&quot;#,##0;-&quot;$&quot;#,##0'` for display as $320,186. Apply to both Yesterday and Last Week value columns.
- **Integer default-format:** Integer count fields should use `default-format='#,##0'` for thousands separator display (e.g., 1,234,567). Always apply to BAN value fields and table measure fields.
- **BAN left alignment:** To left-align BAN text, add `fontalignment='0'` to every `<run>` in the customized-label AND a pane-level `<style><style-rule element='cell'><format attr='text-align' value='left' /></style-rule></style>` after `</customized-label>`. Both are required.

### KPI Card (BAN) Layout Pattern — Full Comparison (DEFAULT)

**Terminology:** "BAN" (Big Ass Number) always means a **KPI card with comparisons** — showing the current value plus arrow, % change, and previous period value. **The default BAN is always a full comparison BAN** (§13.22). Never implement a BAN as a simple standalone number unless explicitly requested.

**Default KPI card layout (4 lines — vs Previous Month + vs Last Year):**
```
Title                          (12pt, #525252)
$42,350                        (22pt bold, #161616)
▲ 5.8% vs PM $40,025           (10pt green #1ea86c arrow+%, 9pt #999999 context)
▼ -2.1% vs LY $43,250          (10pt red #ca1325 arrow+%, 9pt #999999 context)
```

**Conditional coloring uses the split positive/negative technique:** Create separate calculated fields for positive and negative values. Each gets its own `fontcolor` in the customized-label. When positive, negative fields are null (Tableau hides null field references); when negative, positive fields are null. This produces green `#1ea86c` for positive changes and red `#ca1325` for negative changes.

**Each KPI requires these calculated fields (6 per comparison line):**
- Current value: `SUM(IF DATEDIFF("month", [date], TODAY()) = 0 THEN [measure] END)`
- Previous period value: `SUM(IF DATEDIFF("month", [date], TODAY()) = 1 THEN [measure] END)`
- Same period last year: `SUM(IF DATEDIFF("month", [date], TODAY()) = 12 THEN [measure] END)`
- Positive % change: `IF ZN([current]) >= ZN([comparison]) THEN (ZN([current]) - ZN([comparison])) / ABS(ZN([comparison])) END`
- Negative % change: `IF ZN([current]) < ZN([comparison]) THEN (ZN([current]) - ZN([comparison])) / ABS(ZN([comparison])) END`
- Positive arrow (string/nominal): `IF ZN([current]) > ZN([comparison]) THEN "▲" END`
- Negative arrow (string/nominal): `IF ZN([current]) < ZN([comparison]) THEN "▼" END`

**Customized-label XML (4-line pattern with split green/red):**
```xml
<customized-label>
  <formatted-text>
    <run fontalignment="0" fontcolor="#525252" fontname="Tableau Medium" fontsize="12">Title</run>
    <run fontalignment="0">Æ&#10;</run>
    <run bold="true" fontalignment="0" fontcolor="#161616" fontname="Tableau Semibold" fontsize="22"><![CDATA[<[ds].[usr:current:qk]>]]></run>
    <run fontalignment="0">Æ&#10;</run>
    <run fontalignment="0" fontcolor="#1ea86c" fontsize="10"><![CDATA[<[ds].[usr:arrow_pm_pos:nk]>]]></run>
    <run fontalignment="0" fontcolor="#1ea86c" fontsize="10"><![CDATA[ <[ds].[usr:pct_pm_pos:qk]>]]></run>
    <run fontalignment="0" fontcolor="#ca1325" fontsize="10"><![CDATA[<[ds].[usr:arrow_pm_neg:nk]>]]></run>
    <run fontalignment="0" fontcolor="#ca1325" fontsize="10"><![CDATA[ <[ds].[usr:pct_pm_neg:qk]>]]></run>
    <run fontalignment="0" fontcolor="#999999" fontsize="9"><![CDATA[ vs PM <[ds].[usr:val_pm:qk]>]]></run>
    <run fontalignment="0">Æ&#10;</run>
    <run fontalignment="0" fontcolor="#1ea86c" fontsize="10"><![CDATA[<[ds].[usr:arrow_ly_pos:nk]>]]></run>
    <run fontalignment="0" fontcolor="#1ea86c" fontsize="10"><![CDATA[ <[ds].[usr:pct_ly_pos:qk]>]]></run>
    <run fontalignment="0" fontcolor="#ca1325" fontsize="10"><![CDATA[<[ds].[usr:arrow_ly_neg:nk]>]]></run>
    <run fontalignment="0" fontcolor="#ca1325" fontsize="10"><![CDATA[ <[ds].[usr:pct_ly_neg:qk]>]]></run>
    <run fontalignment="0" fontcolor="#999999" fontsize="9"><![CDATA[ vs LY <[ds].[usr:val_ly:qk]>]]></run>
  </formatted-text>
</customized-label>
```

**Encodings must list ALL fields used in the label:**
```xml
<encodings>
  <text column="[ds].[usr:current:qk]" />
  <text column="[ds].[usr:pct_pm_pos:qk]" />
  <text column="[ds].[usr:pct_pm_neg:qk]" />
  <text column="[ds].[usr:val_pm:qk]" />
  <text column="[ds].[usr:arrow_pm_pos:nk]" />
  <text column="[ds].[usr:arrow_pm_neg:nk]" />
  <text column="[ds].[usr:pct_ly_pos:qk]" />
  <text column="[ds].[usr:pct_ly_neg:qk]" />
  <text column="[ds].[usr:val_ly:qk]" />
  <text column="[ds].[usr:arrow_ly_pos:nk]" />
  <text column="[ds].[usr:arrow_ly_neg:nk]" />
</encodings>
```

**KPI zone sizing:** A 4-line KPI card (title + big number + vs PM line + vs LY line) needs `fixed-size='110'` to `fixed-size='120'` on the dashboard zone. A 3-line card (single comparison) uses `fixed-size='92'`. Using 72px or less causes text overflow ("###"). The trend sparkline zone below fills the remaining space. See [references/programmatic-twb-learnings.md](references/programmatic-twb-learnings.md) §13.22 for the full pattern.

**Simple BAN (exception — only when explicitly requested):** When a BAN without comparisons is specifically requested, use the minimal pattern from §14.11 of [references/programmatic-twb-learnings.md](references/programmatic-twb-learnings.md). This is NOT the default.

**Sparkline axis cleanup:** Trend sparkline charts must hide the Y-axis header and both axis titles. Add three format entries inside the axis style-rule: (1) title for the rows-scoped measure field set to empty string, (2) title for the cols-scoped date field set to empty string, (3) display for the rows-scoped measure field set to false. This removes the Y-axis title, X-axis title (e.g. "Paid Date [2026]"), and Y-axis tick labels (0K, 50K, etc.). See section 12 of programmatic-twb-learnings for full XML.

**Sparkline template (dual-axis line + area fill):** Each KPI card has a sparkline below it using the same measure twice on rows to create a dual-axis overlay — a line on top and a shaded area behind. Match the Superstore pattern:

```xml
<worksheet name='Metric Sparkline'>
  <table>
    <view>
      <datasources><datasource caption='DS Caption' name='ds_name' /></datasources>
      <datasource-dependencies datasource='ds_name'>
        <!-- CY measure calc + date field + column-instances -->
      </datasource-dependencies>
      <aggregation value='true' />
    </view>
    <style>
      <style-rule element='axis'>
        <format attr='display' class='1' field='[ds_name].[usr:cy_measure:qk]' scope='rows' value='false' />
        <encoding attr='space' class='1' field='[ds_name].[usr:cy_measure:qk]' field-type='quantitative' fold='true' scope='rows' synchronized='true' type='space' />
        <format attr='display' class='0' field='[ds_name].[usr:cy_measure:qk]' scope='rows' value='false' />
        <format attr='title' class='0' field='[ds_name].[tmn:date_field:qk]' scope='cols' value='' />
        <format attr='display' class='0' field='[ds_name].[tmn:date_field:qk]' scope='cols' value='false' />
      </style-rule>
      <style-rule element='table'>
        <format attr='show-null-value-warning' value='false' />
      </style-rule>
      <style-rule element='gridline'>
        <format attr='stroke-size' scope='rows' value='0' />
        <format attr='line-visibility' scope='rows' value='off' />
      </style-rule>
      <style-rule element='zeroline'>
        <format attr='stroke-size' scope='cols' value='0' />
        <format attr='line-visibility' scope='cols' value='off' />
        <format attr='stroke-size' scope='rows' value='0' />
        <format attr='line-visibility' scope='rows' value='off' />
      </style-rule>
      <style-rule element='table-div'>
        <format attr='stroke-size' scope='rows' value='0' />
        <format attr='line-visibility' scope='rows' value='off' />
        <format attr='stroke-size' scope='cols' value='0' />
        <format attr='line-visibility' scope='cols' value='off' />
      </style-rule>
    </style>
    <panes>
      <pane selection-relaxation-option='selection-relaxation-allow'>
        <view><breakdown value='auto' /></view>
        <mark class='Automatic' />
        <customized-tooltip>
          <formatted-text>
            <run><![CDATA[<[ds_name].[tmn:date_field:qk]>]]></run>
            <run bold='true'><![CDATA[ | <[ds_name].[usr:cy_measure:qk]>]]></run>
          </formatted-text>
        </customized-tooltip>
      </pane>
      <pane id='1' selection-relaxation-option='selection-relaxation-allow' y-axis-name='[ds_name].[usr:cy_measure:qk]' y-index='1'>
        <view><breakdown value='auto' /></view>
        <mark class='Automatic' />
        <customized-tooltip>
          <formatted-text>
            <run><![CDATA[<[ds_name].[tmn:date_field:qk]>]]></run>
            <run bold='true'><![CDATA[ | <[ds_name].[usr:cy_measure:qk]>]]></run>
          </formatted-text>
        </customized-tooltip>
        <style>
          <style-rule element='mark'>
            <format attr='mark-labels-cull' value='true' />
            <format attr='mark-labels-show' value='false' />
          </style-rule>
        </style>
      </pane>
      <pane id='2' selection-relaxation-option='selection-relaxation-allow' y-axis-name='[ds_name].[usr:cy_measure:qk]'>
        <view><breakdown value='auto' /></view>
        <mark class='Area' />
        <customized-tooltip>
          <formatted-text>
            <run><![CDATA[<[ds_name].[tmn:date_field:qk]>]]></run>
            <run bold='true'><![CDATA[ | <[ds_name].[usr:cy_measure:qk]>]]></run>
          </formatted-text>
        </customized-tooltip>
        <style>
          <style-rule element='mark'>
            <format attr='mark-color' value='#dedede' />
          </style-rule>
        </style>
      </pane>
    </panes>
    <rows>([ds_name].[usr:cy_measure:qk] + [ds_name].[usr:cy_measure:qk])</rows>
    <cols>[ds_name].[tmn:date_field:qk]</cols>
  </table>
</worksheet>
```

Key rules: (1) Same measure twice in rows with `+` and parentheses for dual-axis. (2) `synchronized='true'` on class 1 axis encoding is REQUIRED. (3) Both Y-axes hidden (`display='false'`). (4) Area pane uses `mark-color='#dedede'` for light gray fill. (5) All gridlines, zerolines, table-divs off. (6) `show-null-value-warning='false'` on table style. (7) Sparkline zone uses `layout-cache` with `minheight='100' minwidth='100' type-h='scalable' type-w='scalable'`.

## Self-Learning from Tableau Desktop

When the user modifies a generated TWB in Tableau Desktop and asks you to "learn from" a worksheet, follow this procedure:

### Procedure

1. **Read the modified worksheet** from the saved TWB file.
2. **Compare against unmodified worksheets** in the same file (or the generator code's expected output).
3. **Identify new or changed XML elements** — focus on `<style-rule>`, `<format>`, zone attributes, and structural patterns.
4. **Document the pattern** in `references/programmatic-twb-learnings.md` under the next available §25.x subsection.
5. **Update the generator code** (style functions, builder functions) to apply the pattern to all worksheets.
6. **Update this SKILL.md** — add a one-line summary to the "Critical Structural Rules" section.
7. **Regenerate and verify** — re-run the generator and confirm `Validation PASSED` + the fix propagates.

### Key Principle

Tableau Desktop is the source of truth for valid XML. When your generated XML doesn't produce the expected visual result, ask the user to make the change manually in one worksheet, save the file, and tell you which worksheet to learn from. The diff between your generated version and Tableau's saved version reveals the correct XML pattern.

### What to Look For in Diffs

| Category | What Tableau adds/changes |
|----------|--------------------------|
| Field labels | `<style-rule element="worksheet">` with `display-field-labels` |
| Axis hiding | Per-field `<format attr="display" class="0" field="..." scope="..." value="false" />` on `axis` element |
| Title hiding | `show-title="false"` on dashboard `<zone>` |
| Formatting | New `<style-rule>` elements or `<format>` attrs |
| Layout | Zone attributes, `fixed-size`, `layout-cache` changes |
| Mark config | `<mark>`, `<encodings>`, `<customized-label>` structure |

### History of Self-Learned Patterns

| §Ref | Pattern | Learned from |
|------|---------|-------------|
| §25.9 | `display-field-labels` on `worksheet` element | User fixed "Customers By Region" |
| §25.10 | Per-field axis display:false | User fixed "Customers By Region" |
| §28.1 | zone-style must be last child in layout containers | D2E8DA72 on UA dashboard load |
| §28.2 | No space-separated measures on shelves | Malformed expression on text tables & combined charts |
| §28.3 | Cross-referenced calcs need `usr:` derivation | SUM on AGG fields in BANs |
| §28.4 | Sparklines need raw fields, not BAN calcs | Single-dot sparklines in UA dashboard |
| §28.5 | fit-width zoom for tables with many rows | Top Campaigns table |
| §28.6 | Month-Trunc for date axes, not discrete None | Month field showing as text labels |
| §28.7 | Boolean date-range filters with `#date#` literals | Tab 4 filter from 2025 |
| §28.12 | Dual-axis with TWO DIFFERENT measures (parentheses+plus) | User merged actual+goal in Desktop |

## Creating Visualizations

### Bar Chart
```xml
<worksheet name='Sales by Category'>
  <table>
    <view>
      <datasources><datasource name='MyData'/></datasources>
    </view>
    <style/>
    <panes>
      <pane selection-relaxation-option='selection-relaxation-allow'>
        <view><breakdown value='auto'/></view>
        <mark class='Bar'/>
      </pane>
    </panes>
    <rows>[MyData].[sum:Sales:qk]</rows>
    <cols>[MyData].[none:Category:nk]</cols>
  </table>
</worksheet>
```

### Line Chart (Time Series)
```xml
<rows>[MyData].[sum:Sales:qk]</rows>
<cols>[MyData].[yr:OrderDate:ok]</cols>
<mark class='Line'/>
```

### Scatter Plot
```xml
<rows>[MyData].[sum:Profit:qk]</rows>
<cols>[MyData].[sum:Sales:qk]</cols>
<mark class='Circle'/>
```

## Filters

**Important:** String values in filters must use XML entity `&quot;` (not literal quotes). See [references/xml-schema-and-structure.md](references/xml-schema-and-structure.md) for full filter reference (categorical, quantitative, relative date, context, top N, slices/cards).

**Date filter on dashboard:** When adding a date quick filter to a dashboard (Filters Container), use the **continuous date** `[none:FieldName:qk]` for the relative-date filter, worksheet slices, and dashboard filter zone `param`; use `period-type` (not `period-type-v2` which causes D2E8DA72 in generated files) and `include-future='true'` (required — `'false'` causes A1E47F55); and for the dashboard filter zone use no `mode` and `values='database'`. See **[references/filters-and-parameters.md](references/filters-and-parameters.md)** for the full pattern.

### Categorical Filter
```xml
<filter class='categorical' column='[MyData].[none:Region:nk]'>
  <groupfilter function='member' level='[none:Region:nk]' member='&quot;East&quot;'/>
</filter>
```

### Range Filter (Quantitative)
```xml
<filter class='quantitative' column='[MyData].[Sales]'>
  <min>1000</min>
  <max>50000</max>
</filter>
```

## Python Usage

```python
import xml.etree.ElementTree as ET

# Read
tree = ET.parse('workbook.twb')
root = tree.getroot()

# Find datasources
for ds in root.findall('.//datasource'):
    print(ds.get('name'))

# Find worksheets
for ws in root.findall('.//worksheet'):
    print(ws.get('name'))

# Modify and save
tree.write('modified.twb', encoding='utf-8', xml_declaration=True)
```

## Reference Files

### Core XML and Generation
- **[references/xml-schema-and-structure.md](references/xml-schema-and-structure.md)** - **TWB XML schema reference** — Root structure, datasources, columns, column-instance naming, worksheets (table element ordering), parameters (`param-domain-type`: `any`/`list`/`range`), filters, dashboard containers (`type-v2`), actions, windows, metadata records (type code table), minimal viable template, generation best practices
- **[references/error-codes-and-pitfalls.md](references/error-codes-and-pitfalls.md)** - **Error code lookup and generation pitfalls** — All Tableau error codes (D2E8DA72, A1E47F55, 018B7D29, 2805CF18): element ordering, invalid attributes, undeclared elements, Custom SQL pitfalls, formula pitfalls, format attribute pitfalls, generated-TWB-only pitfalls
- **[references/programmatic-twb-learnings.md](references/programmatic-twb-learnings.md)** - **Validated learnings journal** — Living document of all validated TWB generation patterns: §1-5 root/datasources/calcs/column-instances/worksheets, §11 user-created calc patterns, §12 BAN+sparkline, §13 structural rules, §14 Custom SQL/direct-connection, §15 published DS/parameters/Measure Names/DZV/paramctrl/date filters, §24 KPI Tracking Revamp, §25 Desktop-learned patterns

### Data Connections
- **[references/connections-and-datasources.md](references/connections-and-datasources.md)** - **All data source connection patterns** — Published (sqlproxy) and direct (federated), Databricks attributes (v-http-path), Custom SQL with metadata-records, other database connectors, mixed workbook pattern, Python generation template, authentication, extract vs live
- **[references/databricks-connection-config.md](references/databricks-connection-config.md)** - **Internal Databricks connection config** — Org-specific server URL, warehouse HTTP path, catalog, schema values
- **[references/revenue-view-datasource-example.xml](references/revenue-view-datasource-example.xml)** - **Production datasource XML template** — Complete Revenue view datasource with sqlproxy connection, calculations, and metadata-records

### Calculated Fields and Functions
- **[references/calculated-fields-and-lod.md](references/calculated-fields-and-lod.md)** - **Calculated fields and LOD reference** — Where calcs live, minimal column pattern, XML encoding, derivation rules, parameters, table calcs, LOD with scope-isolation, format defaults, folder organization, dashboard types, BAN/KPI calc patterns, YoY, dynamic period comparison, measure/dimension swapper
- **[references/tableau-functions-reference.md](references/tableau-functions-reference.md)** - **Tableau function catalog** — Complete reference: Number, String, Date, Type Conversion, Logical, Aggregate, Table Calculations, LOD, Spatial, User, RAWSQL. Use instead of SQL syntax.

### Dashboard Layout and Design
- **[references/dashboard-layout-and-zones.md](references/dashboard-layout-and-zones.md)** - **Dashboard zones, layout, and visibility** — Zone element (type-v2), coordinate system, container hierarchy, zone styling, default desktop layout (1300x900), sidebar navigation, show/hide buttons (Desktop-only), Dynamic Zone Visibility (datagraph), DZV+parameter actions, info button pattern, DZV programmatic implementation
- **[references/dashboard-design-best-practices.md](references/dashboard-design-best-practices.md)** - **Dashboard UX/design guidelines** — Sizing, visual hierarchy, color system, typography, KPI card anatomy, chart selection, filter placement, tooltip design, clean design techniques, accessibility, device layouts, dashboard templates

### Visualizations and Charts
- **[references/visualizations-and-charts.md](references/visualizations-and-charts.md)** - **Chart type XML patterns** — All mark types, reference/trend lines, encodings, customized tooltips/labels, style rules, sorting. All examples use correct rows/cols placement under table.
- **[references/kpi-cards-and-trends.md](references/kpi-cards-and-trends.md)** - **KPI cards, trend indicators, and navigation** — BAN anatomy, split positive/negative technique, Flerlage Twins technique, sparkline companions, shape trend indicators, zero-calc format alternative, map layers+KPI, navigation sidebar patterns, color palettes, period comparisons

### Filters and Parameters
- **[references/filters-and-parameters.md](references/filters-and-parameters.md)** - **Filter and parameter patterns** — Filter hierarchy, categorical/quantitative/relative-date/context/top-N filters, slices, quick-filter styling, dashboard filter zones, date filter on dashboard, parameter-driven date filter, valid format attributes

### External APIs
- **[references/rest-api.md](references/rest-api.md)** - **Tableau Server/Cloud REST API** — Authentication, publishing, downloading, datasources, projects, permissions, extracts, views, subscriptions, webhooks, jobs
- **[references/hyper-api.md](references/hyper-api.md)** - **Hyper API** — Creating .hyper extracts: table definition, inserting/reading/updating data, multi-table, performance, publishing

## Tableau Server REST API

The REST API uses `tsRequest`/`tsResponse` XML format (separate from TWB XML).

**API Version:** 3.28 (Tableau Server 26.1)

**API Schema:** https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_schema.htm

**XSD:** https://help.tableau.com/samples/en-us/rest_api/ts-api_3_28.xsd

### Sign In
```xml
POST /api/3.28/auth/signin

<tsRequest>
  <credentials name="user" password="pass">
    <site contentUrl="my-site"/>
  </credentials>
</tsRequest>
```

### Publish Workbook
```bash
POST /api/3.28/sites/{site-id}/workbooks?overwrite=true
Content-Type: multipart/mixed; boundary=boundary123
X-Tableau-Auth: {token}

# Request includes tsRequest XML + binary .twbx file
```

### Common Operations
| Operation | Method | Endpoint |
|-----------|--------|----------|
| Sign In | POST | `/auth/signin` |
| List Projects | GET | `/sites/{site-id}/projects` |
| Publish Workbook | POST | `/sites/{site-id}/workbooks` |
| Download Workbook | GET | `/sites/{site-id}/workbooks/{id}/content` |
| Refresh Extract | POST | `/sites/{site-id}/workbooks/{id}/refresh` |
| Query Data Source | GET | `/sites/{site-id}/datasources/{id}` |

### Python with tableauserverclient
```python
import tableauserverclient as TSC

auth = TSC.PersonalAccessTokenAuth('token-name', 'token-secret', 'site-id')
server = TSC.Server('https://server.com', use_server_version=True)

with server.auth.sign_in(auth):
    # Download workbook
    server.workbooks.download('workbook-id', filepath='/tmp/workbook.twbx')
    
    # Publish workbook
    wb = TSC.WorkbookItem(project_id='project-id', name='My Workbook')
    server.workbooks.publish(wb, '/path/to.twbx', mode=TSC.Server.PublishMode.Overwrite)
```

See [references/rest-api.md](references/rest-api.md) for complete API documentation.

## Hyper API (Extract Creation)

Create .hyper extract files programmatically:

```bash
pip install tableauhyperapi
```

```python
from tableauhyperapi import (
    HyperProcess, Telemetry, Connection, CreateMode,
    TableDefinition, TableName, SqlType, Inserter
)

with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    with Connection(hyper.endpoint, 'data.hyper', CreateMode.CREATE_AND_REPLACE) as conn:
        # Define table
        table = TableDefinition(TableName('Extract', 'Sales'), columns=[
            TableDefinition.Column('Region', SqlType.text()),
            TableDefinition.Column('Sales', SqlType.double()),
        ])
        conn.catalog.create_schema('Extract')
        conn.catalog.create_table(table)
        
        # Insert data
        with Inserter(conn, table) as inserter:
            inserter.add_rows([['East', 1500.0], ['West', 2300.5]])
            inserter.execute()
```

See [references/hyper-api.md](references/hyper-api.md) for complete Hyper API documentation.

## Official Tableau GitHub Repositories

| Repository | Purpose | URL |
|------------|---------|-----|
| **server-client-python** | REST API Python client (TSC) | https://github.com/tableau/server-client-python |
| **document-api-python** | Modify TWB/TDS files | https://github.com/tableau/document-api-python |
| **rest-api-samples** | REST API examples | https://github.com/tableau/rest-api-samples |
| **tableau-mcp** | MCP server for AI integration | https://github.com/tableau/tableau-mcp |
| **tableau_langchain** | LangChain tools for Tableau | https://github.com/tableau/tableau_langchain |

### Tableau MCP (Model Context Protocol)
For AI agent integration with Tableau - **automatically fetch published data source information**:

```json
{
  "mcpServers": {
    "tableau": {
      "command": "npx",
      "args": ["-y", "@tableau/mcp-server@latest"],
      "env": {
        "SERVER": "https://your-tableau-cloud.com",
        "SITE_NAME": "your_site",
        "PAT_NAME": "your_pat_name",
        "PAT_VALUE": "your_pat_value"
      }
    }
  }
}
```

**MCP Tools Available:**
- `list-datasources` - List all published data sources (with optional filters)
- `get-datasource-metadata` - Get column information and structure for a specific data source
- `search-content` - Search for data sources by name
- `query-datasource` - Query data from a published data source

**Important:** MCP `list-datasources` does NOT return `contentUrl` (the URL-safe name needed for TWB `<repository-location id>` and `<connection dbname>`). Use `tableauserverclient` (`ds.content_url`), browser URL, or an existing TWB to find it. See §15.1 in [references/programmatic-twb-learnings.md](references/programmatic-twb-learnings.md).

**Example: Get Data Source Info via MCP**
```python
# MCP automatically provides:
# - Exact data source names
# - Column metadata (names, types, roles)
# - Revision numbers
# - Server and site information
# This eliminates manual lookup and ensures accuracy
```

### LangChain Integration
```python
from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

analyze_datasource = initialize_simple_datasource_qa(
    domain='https://your-tableau-cloud.com',
    site='your_site',
    jwt_client_id='connected_app_client_id',
    jwt_secret_id='connected_app_secret_id', 
    jwt_secret='connected_app_secret',
    datasource_luid='datasource_id'
)
```
