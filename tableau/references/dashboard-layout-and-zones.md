# Tableau Dashboard Layout, Zones, and Visibility

Authoritative reference for dashboard zones, coordinates, styling, Desktop-saved show/hide buttons, and Dynamic Zone Visibility (DZV). For generated `.twb` files, use **`type-v2`** on zones and **DZV via the datagraph node system** for show/hide behavior.

**Related:** [programmatic-twb-learnings.md](programmatic-twb-learnings.md) — §15.8 zone styling, §15.10 DZV, §15.11 paramctrl; §15.7 D2E8DA72 patterns including `<button>` / `<toggle-action>` in generated workbooks.

---

## Zone Element

Every dashboard object in a `.twb` — worksheets, containers, text, filters, legends, parameter controls, images — is a `<zone>` nested under `<dashboard><zones>`. Zones form a tree that mirrors the visual layout.

**Core attributes**

| Attribute | Role |
|-----------|------|
| `id` | Unique integer; tab order in published dashboards |
| `name` | For worksheet zones, exact worksheet name; for containers, Item Hierarchy label (often paired with `friendly-name`) |
| `type-v2` | Zone type for current workbooks (standard for generated TWBs) |
| `h`, `w`, `x`, `y` | Position and size in the coordinate system (see below); floating zones use absolute placement |
| `param` | `horz` / `vert` for flow containers; field reference for filters/legends; parameter ref for `paramctrl` |
| `fixed-size` / `is-fixed` | Pixel dimensions for fixed-size zones |
| `show-title` | Whether the worksheet title appears on the dashboard |
| `friendly-name` | Readable label in Item Hierarchy (filters container, viz rows, DZV targets) |
| `hidden` | Static hide (e.g. Stories) |
| `hidden-by-user` | Default hidden state for DZV panels (with datagraph driving visibility) |
| `layout-cache` | Sizing behavior for worksheet zones (`type-h`, `type-w`, `cell-count-*`, `minheight`, etc.) |
| `zone-style` | Border, margin, padding, background (`<format attr='...' value='...'/>`) |

Legacy `type=` appears in older Desktop-saved files. **Generated TWBs should use `type-v2` throughout.**

---

## Zone Types

Common **`type-v2`** values:

| type-v2 | Description |
|---------|-------------|
| `layout-basic` | Root tiled container or major section |
| `layout-flow` | Horizontal (`param='horz'`) or vertical (`param='vert'`) stack |
| `text` | Text object |
| `title` | Dashboard title object (legacy layouts) |
| `bitmap` | Image |
| `color`, `size`, `shape` | Legend types |
| `filter` | Quick filter |
| `paramctrl` | Parameter control |
| `highlighter` | Highlighter |
| `empty` | Spacer |
| `dashboard-object` | Desktop show/hide button host (`<button>` child) |
| `flipboard`, `flipboard-nav` | Story navigation |

Worksheet zones reference the sheet by **`name='<Worksheet Name>'`** without a separate worksheet type in the Desktop layout pattern.

---

## Coordinate System

- **100,000 units = 100%** of the parent container for tiled layout.
- **Root zone:** `x='0' y='0' w='100000' h='100000'`.
- Proportional splits (title row ~8%, content ~92%, filters column ~12%, viz column ~88%) are expressed in the same grid; Desktop may rewrite coordinates on open—**hierarchy and zone types matter most**.

---

## Container Hierarchy

**Wireframe (default desktop pattern)**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ROW 1: DASHBOARD TITLE (full width)                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────────┐
│  HORIZONTAL CONTAINER (full width)                                              │
│  ┌──────────────────┐  ┌──────────────────────────────────────────────────────┐ │
│  │ VERTICAL         │  │ VIZ COLUMN (vertical stack)                          │ │
│  │ (filters)        │  │ Row 1: Key Metrics (full width)                      │ │
│  │                  │  │ Row 2: [Sheet A] | [Sheet B]                         │ │
│  └──────────────────┘  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Zone tree (plain text)**

```
layout-basic (root)
├── layout-flow [param=vert]           ← title then content
│   ├── text (title)
│   └── layout-flow [param=horz]       ← filters | viz
│       ├── layout-flow [param=vert]   ← filters column (fixed width)
│       │   ├── filter
│       │   ├── filter
│       │   └── filter
│       └── layout-flow [param=vert]   ← viz column
│           ├── layout-flow [param=horz]  ← viz row 1
│           ├── layout-flow [param=horz]  ← viz row 2
│           └── layout-flow [param=horz]  ← viz row 3
```

**Levels**

| Level | Role | type-v2 | param |
|-------|------|---------|-------|
| 1 | Root | `layout-basic` | — |
| 2 | Main stack | `layout-flow` | `vert` |
| 3a | Title | `text` | — |
| 3b | Content row | `layout-flow` | `horz` |
| 4a | Filters column | `layout-flow` | `vert` + `fixed-size` width |
| 4b | Viz column | `layout-flow` | `vert` |
| 5 | Viz rows | `layout-flow` | `horz` |

**Parent–child:** Root contains one vertical flow; that flow contains the title and one horizontal flow; the horizontal flow contains exactly two vertical children (filters column, viz column); the viz column contains horizontal flows, each holding worksheet zones.

---

## Zone Styling

Apply **`margin` and `padding` on worksheet zones**, not on `layout-flow` containers—Tableau applies card spacing from the sheet zone’s `zone-style`.

**Two tiers**

| Tier | margin | padding | Typical use |
|------|--------|---------|-------------|
| **Simple** | `12` | `4` | Standard cards (`border-color`, `border-style='solid'`, `border-width='1'`, `background-color='#ffffff'`) |
| **Polished** | `12` | `12` | Higher whitespace, premium card look |

Example (polished card):

```xml
<zone h='11772' id='10' name='Orders' show-title='false' w='16666' x='0' y='4500'>
  <zone-style>
    <format attr='border-color' value='#e6e6e6' />
    <format attr='border-style' value='solid' />
    <format attr='border-width' value='1' />
    <format attr='margin' value='12' />
    <format attr='padding' value='12' />
    <format attr='background-color' value='#ffffff' />
  </zone-style>
</zone>
```

Details and validation: [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §15.8.

---

## Distribute Content Evenly

To make child zones share space equally within a horizontal or vertical container, add `layout-strategy-id='distribute-evenly'` to the parent `layout-flow` zone:

```xml
<zone fixed-size="300" h="20000" id="5" is-fixed="true"
      layout-strategy-id="distribute-evenly"
      param="horz" type-v2="layout-flow"
      w="100000" x="0" y="3000">
  <!-- Child zones automatically share width equally -->
  <zone h="10000" id="6" param="vert" type-v2="layout-flow" w="20000" x="0" y="0">...</zone>
  <zone h="10000" id="7" param="vert" type-v2="layout-flow" w="20000" x="20000" y="0">...</zone>
  <zone h="10000" id="8" param="vert" type-v2="layout-flow" w="20000" x="40000" y="0">...</zone>
</zone>
```

**Key attributes:**
- `layout-strategy-id='distribute-evenly'` — children share space equally
- `is-fixed='true'` — container height/width is fixed
- `fixed-size='300'` — the container's fixed size in pixels

Use `distribute-evenly` on **horizontal** containers for equal-width columns (e.g. KPI banner cards) and on **vertical** containers for equal-height rows (e.g. product card grids).

---

## Fit Entire View

To make a worksheet fill its dashboard zone, set its window viewpoint to `entire-view`:

```xml
<window class="worksheet" name="My Sheet">
  <cards>
    <edge name="left" />
    <edge name="top" />
    <edge name="right" />
    <edge name="bottom" />
  </cards>
  <viewpoint>
    <zoom type="entire-view" />
  </viewpoint>
</window>
```

The `<zoom type="entire-view" />` ensures the worksheet content stretches to fill the available space. Without it, Tableau uses the default "Normal" fit which may leave empty space or show scrollbars.

**When to use:**
- Tables/heatmaps that should fill their container
- Product deep-dive cards in a grid layout
- Any worksheet where scrollbars are unwanted

---

## Rounded Corners

Rounded corners require two components:

**1. Manifest entry** (in `<document-format-change-manifest>`):
```xml
<_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners />
```

**2. Corner radius format** (in `<zone-style>` for each zone):
```xml
<zone-style>
  <format attr="border-color" value="#ebebeb" />
  <format attr="border-style" value="solid" />
  <format attr="border-width" value="1" />
  <format attr="margin" value="6" />
  <format attr="padding" value="4" />
  <format attr="background-color" value="#ffffff" />
  <_.fcp.DashboardRoundedCorners.true...format attr="corner-radius" value="8" />
</zone-style>
```

**Important:** The corner-radius element uses the long prefixed name `_.fcp.DashboardRoundedCorners.true...format`, NOT a plain `<format>` element. Using `<format attr="corner-radius">` causes D2E8DA72 (attribute not in enumeration).

**Post-processing note:** Python's `xml.etree.ElementTree` escapes the `<` in the element name. Post-process the serialized XML to unescape:
```python
content = content.replace(
    '&lt;_.fcp.DashboardRoundedCorners', '<_.fcp.DashboardRoundedCorners')
content = content.replace(
    '&lt;/_.fcp.DashboardRoundedCorners', '</_.fcp.DashboardRoundedCorners')
```

---

## Default Desktop Dashboard

- **Canvas size:** Fixed layout commonly **1300×900** (e.g. `minwidth`/`maxwidth` 1300, `minheight`/`maxheight` 900, `sizing-mode='fixed'`). Adjust per product; Superstore-style sidebars may use **1500×900**.
- **Structure:** Title row → one horizontal container → vertical filters column | vertical viz column (see wireframe above).
- **Color palette (backgrounds)**

| Area | Hex | Notes |
|------|-----|--------|
| Header (title + filters column) | `#6F91DB` | Groups “controls” |
| Main canvas (viz column) | `#F0F3FA` | Behind worksheet cards |
| Worksheet cards | `#FFFFFF` | Per viz |

Title: `background-color='#6F91DB'`, margin, no border. Filters column: same header color; place **`zone-style` after all child zones** (schema order). Individual filter zones: light margin (e.g. `4`) on the colored header. Worksheet zones: card border `#e0e0e0` or `#e6e6e6`, white fill, simple or polished margin/padding tier.

**Worksheet titles (embedded)**

For chart worksheets, set title via **worksheet** `layout-options` / `formatted-text` (e.g. `fontname='Tableau Medium'`). For KPI/text-only sheets, `show-title='false'` on the dashboard zone and omit the worksheet title block.

```xml
<layout-options>
  <title>
    <formatted-text>
      <run fontname='Tableau Medium'>Sheet Name</run>
    </formatted-text>
  </title>
</layout-options>
```

**Row header alignment (bar charts)** — left-align category labels:

```xml
<style-rule element='label'>
  <format attr='text-align' field='[datasource].[none:field_name:nk]' value='left' />
</style-rule>
```

---

## Sidebar Navigation Layout Variant

**Reference:** Superstore Annual Financial Report pattern (`superstore_annual_financial_report.twb`).

Fixed-width **left sidebar** (~160px, e.g. `#f5eced`) for nav text, `paramctrl`, download/credits—instead of a separate filters column beside the title row.

**Wireframe**

```
┌──────┬─────────────────────────────────────────────────────────────┐
│ S.   │  Dashboard title                                            │
│ NAV  ├─────────────┬─────────────┬─────────────┬─────────────────│
│ CTRL │  BAN        │ BAN         │ BAN         │ BAN             │
│      │  Sparkline  │ Sparkline   │ Sparkline   │ Sparkline       │
│ DL   ├─────────────┴─┬───────────┴─────────────┴─────────────────│
│ ©    │  Breakdowns   │  Map + trend                              │
└──────┴───────────────┴─────────────────────────────────────────────┘
```

**Hierarchy sketch**

```
layout-basic
└── layout-flow [horz] "Main Row"
    ├── layout-flow [vert, fixed-size=160] "Sidebar"
    │   ├── text (logo), spacers, nav buttons, paramctrl, download, footer
    └── layout-flow [vert] "Main Content"
        ├── layout-flow [horz] header + KPI rows (nested card layout-flows per KPI)
        └── layout-flow [horz] breakdown column | map/trend column
```

KPI cards: vertical `layout-flow` per card; BAN `fixed-size` height; sparkline flexible. `show-title='false'` on worksheet zones; titles via worksheet `layout-options`.

---

## Checklist for New Dashboards

- [ ] Root `layout-basic` with zone-style (background, margin).
- [ ] First child vertical flow: full-width title, then one horizontal flow.
- [ ] Horizontal flow has two children: vertical filters (left), vertical viz (right).
- [ ] Filters column: `param='vert'`, `fixed-size` width, `friendly-name='Filters Container'`.
- [ ] Viz column: `param='vert'`; each child a horizontal flow (viz row).
- [ ] Worksheet zones: `name` matches worksheet; `layout-cache` + `zone-style` with simple or polished tier.
- [ ] KPI/text-only zones: `show-title='false'` where titles are omitted on the worksheet.
- [ ] Containers named with `friendly-name` for Item Hierarchy (Title, Content Row, Viz Column, rows).
- [ ] Dashboard-level `<datasources>` / `<datasource-dependencies>` when filters need dashboard-resolved fields.

**Collection Overview** (user-adjusted): see [default-desktop-dashboard-layout.md](default-desktop-dashboard-layout.md) for filter zone table, BAN + Sparkline row, and net collection BAN period logic.

---

## Show/Hide Buttons

**Mechanism:** `type-v2='dashboard-object'` zone with `<button>` and `<toggle-action>` text action.

**Placement:** Button zone is a **sibling of the root** layout zone—both direct children of `<zones>`.

**`toggle-action` payload** (string content):

- `tabdoc:toggle-button-click-action`
- `window-id` — dashboard **window** `simple-id` UUID (from `<window class='dashboard'>` → `<simple-id uuid='{...}'/>`), braces included, encoded as `&quot;{GUID}&quot;` in XML when needed
- `zone-id` — the button zone’s `id`
- `zone-ids` — JSON-style array of target zone ids, e.g. `[27]` or `[27,28,29]` for multiple containers

**Example (Desktop-saved style)**

```xml
<zones>
  <zone id='4' type-v2='layout-basic'>...</zone>
  <zone h='2000' id='118' type-v2='dashboard-object' w='1655' x='45448' y='14167'>
    <button action=''>
      <toggle-action>tabdoc:toggle-button-click-action window-id=&quot;{FADDCE12-683B-43EE-A42B-4E0DE2CEF372}&quot; zone-id=&quot;118&quot; zone-ids=[5]</toggle-action>
      <button-visual-state />
      <button-visual-state />
    </button>
  </zone>
</zones>
```

**Generated TWBs:** Tableau’s schema for freshly generated files does not accept `<button>` / `<toggle-action>` (load error **D2E8DA72** — see [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §15.7). **Use DZV (datagraph + parameter + `paramctrl`)** for programmatic show/hide.

---

## Dynamic Zone Visibility (DZV)

DZV shows or hides zones based on a **boolean** field (parameter, calc, or LOD) that returns a **single value** and is **independent of the viz**.

**Mechanism:** Workbook-level **`<datagraph>`** (after `<windows>`), not visibility attributes on zones. Nodes and edges connect a boolean field to each controlled zone.

**Manifest** (among others):

```xml
<ZoneVisibilityControl />
<DatagraphCoreV1 />
<DatagraphNodeDashboardZoneVisibilityV1 />
<DatagraphNodeSingleValueFieldV1 />
```

**Datagraph pattern**

```xml
<datagraph>
  <graph>
    <properties>
      <default-execution-subgraph-guid value='fcddcc42-5057-447d-9958-5350e350033e' />
    </properties>
    <node-execution-subgraphs>
      <pair execution-subgraph-guid='fcddcc42-5057-447d-9958-5350e350033e'
            node-guid='2a21e0dc-e617-445c-bbaf-5f5e2909de70' />
      <pair execution-subgraph-guid='fcddcc42-5057-447d-9958-5350e350033e'
            node-guid='fcbab04b-f8c1-41e2-92d7-7bd9796dbdd6' />
    </node-execution-subgraphs>
    <nodes>
      <dashboard-zone-visibility-node
          dashboard-identifier='{A84CA6BB-1D52-43D7-B1AF-202C36982290}'
          node-guid='2a21e0dc-e617-445c-bbaf-5f5e2909de70'
          visibility-input-guid='603d7bc1-1c70-4f13-aa74-18c660c2145c'
          zone-id='152' />
      <single-value-field-node
          fieldname='[Sample - Superstore].[Calculation_1913466913119399946]'
          fieldname-input-guid='0ee78253-cd6d-478b-8796-923f9cd8c189'
          node-guid='fcbab04b-f8c1-41e2-92d7-7bd9796dbdd6'
          value-output-guid='df493ecd-8725-442c-acd3-336fda475ce1' />
    </nodes>
    <edges>
      <edge from='df493ecd-8725-442c-acd3-336fda475ce1'
            to='603d7bc1-1c70-4f13-aa74-18c660c2145c' />
    </edges>
    <pin-values />
  </graph>
</datagraph>
```

- `dashboard-zone-visibility-node`: `zone-id`, `visibility-input-guid`, `dashboard-identifier` matching the dashboard window UUID.
- `single-value-field-node`: boolean field reference; `value-output-guid` connects via `<edge>` to `visibility-input-guid`.
- **Target zones:** default hidden state uses **`hidden-by-user='true'`** on the panel root **and** every descendant zone; **one visibility node per zone** in the datagraph, all fed by the same boolean field node.

**Boolean calc example**

```xml
<column caption='Open ?' datatype='boolean'
        name='[Calculation_1913466913119399946]'
        role='dimension' type='nominal'>
  <calculation class='tableau' formula='[Parameters].[Parameter 4]=&apos;Open&apos;' />
</column>
```

**GUIDs:** Use `uuid.uuid4()` for execution subgraph, node GUIDs, and input/output GUIDs when generating XML.

---

## DZV + Parameter Actions Pattern

**Flow:** Worksheet “button” marks → **`<edit-parameter-action>`** → string parameters → boolean calc → **datagraph** visibility.

**Parameters (example):**

- **Measure Name** (`Parameter 3`): which KPI to show in the drilldown.
- **Open / Close** (`Parameter 4`): `'Open'` / `'Close'` for panel visibility.

```xml
<column caption='Measure Name' datatype='string' name='[Parameter 3]'
        param-domain-type='list' role='measure' type='nominal' value='&quot;Profit&quot;'>
  <calculation class='tableau' formula='&quot;Profit&quot;' />
  <members>
    <member value='&quot;Sales&quot;' />
    <member value='&quot;Profit&quot;' />
  </members>
</column>
<column caption='Open / Close' datatype='string' name='[Parameter 4]'
        param-domain-type='list' role='measure' type='nominal' value='&quot;Close&quot;'>
  <calculation class='tableau' formula='&quot;Close&quot;' />
  <members>
    <member value='&quot;Open&quot;' />
    <member value='&quot;Close&quot;' />
  </members>
</column>
```

Each KPI sheet can fire parameter actions to set **Open** and the **measure**; a Close sheet sets **Close**. The boolean field used in `single-value-field-node` evaluates those parameters. Button zones on the dashboard use normal worksheet zones with tight `zone-style` (e.g. zero border, small fixed height).

---

## Info Button Pattern

Uses **Desktop show/hide** (`dashboard-object` + `<button>`), not DZV—suitable for static documentation panels in Desktop-saved workbooks.

**Toggle button** (info icon):

```xml
<zone h='2718' id='126' type-v2='dashboard-object' w='2222' x='88056' y='2136'>
  <button action='' active-visual-state-index='1'>
    <toggle-action>tabdoc:toggle-button-click-action
      window-id=&quot;{98B88022-D3AE-4D68-A927-FE7880D304FD}&quot;
      zone-id=&quot;126&quot;
      zone-ids=[123]</toggle-action>
    <button-visual-state />
    <button-visual-state>
      <image-path>Image/icons8-info-96 (1).png</image-path>
    </button-visual-state>
  </button>
</zone>
```

**Panel:** `hidden-by-user='true'`, white background, **1px gray border**, **`padding='30'`**, documentation copy in nested `text` zones.

---

## DZV Programmatic Implementation

For **generated** TWBs: **`paramctrl`** + **workbook-level `<datagraph>`** + **Show/Hide string parameter** + **boolean calc** (see [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §15.10, §15.11).

**Principles**

- `<datagraph>` is a **direct child of `<workbook>`**, **after `<windows>`** (inside `<dashboard>` causes D2E8DA72).
- Floating DZV panel: **sibling** of root `layout-basic`, direct under `<zones>`, absolute `x`/`y`/`w`/`h`.
- `hidden-by-user='true'` on **all** zones in the panel (root and children).
- One `dashboard-zone-visibility-node` per hidden zone; edges from one `single-value-field-node` output to each visibility input.

**String parameter + boolean**

```xml
<column caption='Show Events' datatype='string' name='[Show Events]'
        param-domain-type='list' role='measure' type='nominal' value='&quot;Hide&quot;'>
  <calculation class='tableau' formula='&quot;Hide&quot;' />
  <members>
    <member alias='Show' value='&quot;Show&quot;' />
    <member alias='Hide' value='&quot;Hide&quot;' />
  </members>
</column>
```

```xml
<column caption='Events Panel Visible' datatype='boolean'
        name='[Calculation_XXXX]' role='measure' type='nominal'>
  <calculation class='tableau' formula="[Parameters].[Show Events] = 'Show'" />
</column>
```

**Zones snippet**

```xml
<zones>
  <zone id='2' type-v2='layout-basic'>
    <zone param='vert' type-v2='layout-flow'>
      <zone is-fixed='true' fixed-size='28'
            param='[Parameters].[Show Events]' type-v2='paramctrl' />
      <!-- main content -->
    </zone>
  </zone>
  <zone h='78000' id='17' hidden-by-user='true'
        param='vert' type-v2='layout-flow'
        w='92000' x='4000' y='16000'
        friendly-name='Events Drilldown Panel'>
    <zone hidden-by-user='true' type-v2='text'>...</zone>
    <zone hidden-by-user='true' param='horz' type-v2='layout-flow'>
      <zone hidden-by-user='true' name='Chart 1' />
      <zone hidden-by-user='true' name='Chart 2' />
    </zone>
    <zone-style>
      <format attr='background-color' value='#ffffff' />
      <format attr='border-color' value='#c0c0c0' />
      <format attr='border-style' value='solid' />
      <format attr='border-width' value='2' />
      <format attr='padding' value='12' />
    </zone-style>
  </zone>
</zones>
```

**Workbook-level datagraph** (abbreviated; full pattern in §15.10):

```xml
<datagraph>
  <graph>
    <properties>
      <default-execution-subgraph-guid value='EXEC-GUID' />
    </properties>
    <node-execution-subgraphs>
      <pair execution-subgraph-guid='EXEC-GUID' node-guid='FIELD-NODE-GUID' />
      <pair execution-subgraph-guid='EXEC-GUID' node-guid='VIZ-NODE-1-GUID' />
    </node-execution-subgraphs>
    <nodes>
      <single-value-field-node
          fieldname='[datasource_name].[Calculation_XXXX]'
          fieldname-input-guid='FI-GUID'
          node-guid='FIELD-NODE-GUID'
          value-output-guid='VO-GUID' />
      <dashboard-zone-visibility-node
          dashboard-identifier='{DASHBOARD-UUID}'
          node-guid='VIZ-NODE-1-GUID'
          visibility-input-guid='VI-1-GUID'
          zone-id='17' />
    </nodes>
    <edges>
      <edge from='VO-GUID' to='VI-1-GUID' />
    </edges>
    <pin-values />
  </graph>
</datagraph>
```

Manifest: `DatagraphCoreV1`, `DatagraphNodeDashboardZoneVisibilityV1`, `DatagraphNodeSingleValueFieldV1`, `ZoneVisibilityControl`.

---

## How Show/Hide and DZV Differ

| Aspect | Show/Hide button (`dashboard-object`) | Dynamic Zone Visibility (DZV) |
|--------|--------------------------------------|------------------------------|
| **Trigger** | User clicks the button zone | Boolean field value (parameters, calcs, actions) |
| **XML mechanism** | `<button>` + `<toggle-action>` with `zone-ids` | **Datagraph:** `dashboard-zone-visibility-node` + `single-value-field-node` + `<edge>` |
| **Where defined** | Zones under `<dashboard>` | **Workbook-level** `<datagraph>` after `<windows>`; zones use `hidden-by-user` defaults |
| **Visibility logic** | Encoded in toggle-action string | **Graph edges** connect field output to visibility node inputs |
| **Generated TWBs** | Use **DZV + `paramctrl`** | Use **DZV + `paramctrl`** |

**When to use**

- **Desktop-maintained workbook:** Show/hide buttons work for simple toggles (e.g. info panel); DZV for data-driven or action-driven visibility.
- **Programmatic TWB generation:** **DZV datagraph + string parameter + boolean calc + `paramctrl`** — the supported pattern ([programmatic-twb-learnings.md](programmatic-twb-learnings.md) §15.10, §15.11).

---

## Related References

- [dashboard-structure.md](dashboard-structure.md) — Additional layout examples, gridline style, data source field usage
- [default-desktop-dashboard-layout.md](default-desktop-dashboard-layout.md) — Collection Overview filters, BAN row, date filter notes
- [dynamic-zone-visibility-show-hide-buttons.md](dynamic-zone-visibility-show-hide-buttons.md) — Original deep-dive (superseded by this file for layout authority)
- [programmatic-twb-learnings.md](programmatic-twb-learnings.md) — §15.7 D2E8DA72, §15.8 styling, §15.10 DZV, §15.11 paramctrl
