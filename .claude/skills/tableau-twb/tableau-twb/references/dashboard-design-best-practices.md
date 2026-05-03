# Tableau Dashboard Design Best Practices Reference Guide

**Purpose**: A comprehensive reference for AI coding assistants building Tableau dashboards, containing specific values, rules, and patterns for optimal design decisions.

---

## Quick reference: Critical values at a glance

| Category | Setting | Recommended Value |
|----------|---------|-------------------|
| **Dashboard Dimensions** | Desktop standard | 1300 × 900px |
| | Presentation (16:9) | 1600 × 900px |
| | Large desktop | 1920 × 1080px |
| | Laptop safe | 1280 × 720px |
| | Tablet | 1024 × 768px |
| | Phone width | 420px (fit width) |
| **Spacing** | Default object padding | 4px |
| | Container outer padding | 8px |
| | Worksheet outer padding | 16px |
| | Filter/legend padding | 8px |
| | Between major sections | 20-24px |
| **Typography** | Dashboard title | 24-36px, Bold |
| | Section headers | 18-24px, Semi-bold |
| | Chart titles | 14-16px, Semi-bold |
| | Body text | 14-16px, Regular |
| | Axis labels | 10-12px, Regular |
| | Footnotes | 9-11px, Regular |
| **Limits** | Sheets per dashboard | 2-4 recommended, up to 5 for KPI-heavy layouts |
| | KPIs per view | 5-7 maximum |
| | Colors in palette | 6-10 categorical |
| | Target load time | Under 5 seconds |

---

## 1. Dashboard layout and sizing

### Size configuration rules

**Fixed size is recommended** for published dashboards—enables server-side caching and predictable rendering. Use Range sizing only when supporting multiple similar screen sizes.

```
SIZING DECISION TREE:
├── Publishing to Tableau Server/Cloud? → Fixed size (1300×900 or 1600×900)
├── Embedding in web app? → Fixed size matching embed container
├── Multi-device support needed? → Create device-specific layouts
└── Presentations? → 1600×900 (PowerPoint 16:9)
```

**Device breakpoints** determine which layout displays:
- **Desktop**: Smallest viewport dimension > 800px
- **Tablet**: Smallest dimension 501-800px
- **Phone**: Smallest dimension ≤ 500px

### Tiled vs floating objects

**Use tiled layout (default)** for:
- Responsive designs that adapt to size changes
- Maintainable, predictable layouts
- Most dashboard elements

**Use floating layout** for:
- Logos and branding elements
- Overlay annotations
- Elements requiring pixel-precise positioning
- Background images with overlaid worksheets

**Hybrid approach (recommended for complex dashboards)**: Create floating layout containers, then place tiled objects inside them for both precision and structure.

### Container organization patterns

**Standard dashboard structure:**
```
[Tiled Root]
├── [Horizontal Container: Header]
│   ├── Logo (32-40px height)
│   ├── Title (left-aligned or center)
│   └── Global Filters / Timestamp (right-aligned)
├── [Horizontal Container: KPI Row]
│   ├── KPI Card 1
│   ├── KPI Card 2
│   ├── KPI Card 3
│   └── KPI Card 4
├── [Horizontal Container: Main Content]
│   ├── Primary Visualization (60% width)
│   └── Secondary Visualization (40% width)
└── [Horizontal Container: Detail/Footer]
    └── Detail Table or Supporting Chart
```

**Container best practices:**
- Name containers descriptively: "Header Container", "Filter Panel", "Main Content Area"
- Work outside-in when building nested containers
- Use "Distribute Evenly" (right-click container) for equal spacing
- Maximum nesting depth: 3-4 levels for maintainability
- Minimum container collapse size: 30px height or width

### Padding and spacing configuration

Access padding in **Layout pane** for each selected object:
- **Inner padding**: Space between content and border
- **Outer padding**: Space beyond border and background

**Recommended padding configuration:**
```
PRIMARY WORKSHEETS:
  Outer padding: 16px all sides

FILTERS AND LEGENDS:
  Outer padding: 8px all sides

KPI CARDS:
  Inner padding: 16-24px all sides

CONTAINERS:
  Outer padding: 8px (creates gutters between sections)

DASHBOARD EDGES:
  Outer margins: 16-24px from edge
```

---

## 2. Visual hierarchy and reading patterns

### Z-pattern layout (executive/summary dashboards)

Place elements following the natural eye movement: top-left → top-right → diagonal → bottom-left → bottom-right.

```
┌─────────────────────────────────────────────────┐
│ [1-LOGO/TITLE]              [2-FILTERS/NAV]     │
├─────────────────────────────────────────────────┤
│                                                 │
│   [MAIN KPI 1]          [MAIN KPI 2]            │
│              ↘                                  │
├─────────────────────────────────────────────────┤
│   [3-CHART A]           │  [4-CHART B]          │
└─────────────────────────────────────────────────┘

Point 1 & 4 are highest-attention positions
```

**When to use**: Executive dashboards, landing pages, 3-5 visual elements, clear call-to-action

### F-pattern layout (detailed analysis dashboards)

```
┌─────────────────────────────────────────────────┐
│ [HEADER: LOGO - TITLE - NAVIGATION - FILTERS]   │  ← Full horizontal scan
├─────────────────────────────────────────────────┤
│ [KPI 1] [KPI 2] [KPI 3] [KPI 4]                 │  ← Second horizontal scan
├─────────────────────────────────────────────────┤
│ [FILTER    │                                    │
│  SIDEBAR]  │  [MAIN VISUALIZATION]              │  ← Left-side vertical scan
│            │                                    │
├────────────┼────────────────────────────────────┤
│ [NAV]      │  [SECONDARY CHARTS / TABLES]       │
└────────────┴────────────────────────────────────┘
```

**When to use**: Data-heavy dashboards, extensive filtering, detailed analysis

### Visual hierarchy rules

1. **Position**: Upper-left = highest importance
2. **Size**: Larger elements = more important (KPIs larger than detail charts)
3. **Color**: Saturated colors draw attention; use neutral base, accent sparingly
4. **Contrast**: High contrast = high importance
5. **The 5-second rule**: Main message should be understood within 5 seconds

---

## 3. Color system and palettes

### Color usage rules

```
COLOR BUDGET PER DASHBOARD:
├── Background: 1 neutral color (white, light gray)
├── Text: 1-2 colors (black/dark gray, accent for emphasis)
├── Data encoding: Maximum 6 colors for categorical
├── Alerts/Status: 3 colors (red, yellow, green)
└── TOTAL: Maximum 10-12 distinct colors
```

### Recommended color palettes

**Categorical palette (sequential application):**
```
Position 1: #6929c4 (Purple)
Position 2: #1192e8 (Cyan)
Position 3: #005d5d (Teal)
Position 4: #9f1853 (Magenta)
Position 5: #fa4d56 (Red)
Position 6: #198038 (Green)
Position 7: #002d9c (Blue)
Position 8: #b28600 (Yellow/Gold)
```

**Sequential palette (low to high values):**
```
Light → Dark (Blue):
#edf5ff → #d0e2ff → #a6c8ff → #78a9ff → #4589ff → #0f62fe → #0043ce → #002d9c
```

**Diverging palette (negative ← neutral → positive):**
```
Red side: #750e13 → #da1e28 → #ff8389 → #fff1f1
Cyan side: #e5f6ff → #82cfff → #1192e8 → #003a6d
```

**Status/Alert colors (learned from reference dashboards):**

| Status | Google Ads | Global Software | Help Desk | Generic |
|--------|-----------|-----------------|-----------|---------|
| Positive/Good | `#25a156` / `#59a14f` | `#59a14f` | `#819cff` | `#198038` |
| Negative/Bad | `#ef4d93` / `#d1668f` | `#e15759` | `#ff6788` | `#da1e28` |
| Warning | `#cb6e26` / `#fb7c0e` | `#f28e2b` | — | `#ff832b` |
| Neutral | `#d9d9d9` | `#8ace7e` | `#9de1e5` | `#f1c21b` |

**Background colors:**
- Light theme: `#FFFFFF` (white cards) or `#F4F4F4` / `#f8f8f8` (light gray sections)
- Dashboard background: `#e6e6e6` (Google Ads), `#eceff79b` (Help Desk), `#ffffff` (Global Software)
- Dark header: `#3d475f` (Help Desk nav bar)
- Card backgrounds: Always `#ffffff` with subtle borders
- Subtle gridlines: `#E0E0E0`

**Card border colors:**
- `#e8f0f7` (Google Ads — very light blue)
- `#a3bdf1` (Global Software — medium blue)
- `#dbdffd` (Dynamic Zone KPIs — lavender)
- `#e6e6e6` (E-Commerce — neutral gray)

**Primary accent colors (per dashboard style):**

| Style | Primary | Secondary | Muted |
|-------|---------|-----------|-------|
| Blue corporate | `#3c8bd9` | `#444c54` | `#606b76` |
| Indigo modern | `#4d60f3` / `#1f48ff` | `#555555` | `#666666` |
| Navy sidebar | `#6279b8` | `#4e79a7` | `#898989` |
| Dark teal | `#3d475f` / `#364781` | `#011936` | `#3d475f` |

### Colorblind-safe palette (Wong, Nature Methods)

For maximum accessibility, use this 8-color palette:
```
#000000 (Black)
#E69F00 (Orange)
#56B4E9 (Sky Blue)
#009E73 (Bluish Green)
#F0E442 (Yellow)
#0072B2 (Blue)
#D55E00 (Vermillion)
#CC79A7 (Reddish Purple)
```

**Color accessibility rules:**
- Never rely on color alone to convey meaning
- Avoid red-green combinations
- Ensure colors vary in lightness (should work in grayscale)
- Test with color blindness simulators

---

## 4. Typography specifications

### Font family recommendations

**Primary choices** (in order of preference):
1. Tableau Book/Medium (native — used in Dynamic Zone KPIs dashboard)
2. Arial (web-safe — used in Global Software and Help Desk dashboards)
3. Raleway (display — used in Google Ads for titles/headers)
4. Noto Sans (labels — used in Google Ads for body text)
5. Lato (branding text)

**Rules:**
- Use 1-2 font families maximum per dashboard
- Use sans-serif fonts for all data visualization
- Enable tabular figures (monospaced numbers) for data alignment
- **Global font:** Set via `<style-rule element='all'><format attr='font-family' value='...' /></style-rule>`

### Font size hierarchy

```
HIERARCHY (descending importance):
├── Dashboard Title: 24-36px, Bold (700)
├── Section Headers: 14-15px, Bold (e.g., "SUMMARY | DETAIL")
├── Chart/KPI Titles: 10-12px, Bold
├── KPI Values (BAN): 16-24px, Bold
├── Body Text / Labels: 9-11px, Regular
├── Axis Labels: 8-10px, Regular
├── Comparison/Context: 8-9px, Regular
└── Footnotes/Branding: 8-11px, Regular

SCALING RATIO: 1.309 (half-golden ratio)
Example: 8px → 10px → 14px → 18px → 24px
```

### Typography patterns from reference dashboards

| Dashboard | Title | Section Headers | KPI Values | KPI Labels | Comparison Text | Axis |
|-----------|-------|-----------------|------------|------------|-----------------|------|
| **Google Ads** | Raleway 36pt `#888f96` | Raleway 14pt bold `#3c8bd9` | 16pt bold `#3c8bd9` | Noto Sans 12pt bold `#444c54` | 8pt `#606b76` | 8pt `#606b76` |
| **Global Software** | Arial 12pt `#898989` | Arial 10pt `#898989` | Arial 20pt bold `#555555` | Arial 10pt `#898989` | Arial 10pt `#59a14f`/`#e15759` | Arial 9pt `#898989` |
| **Dynamic Zone KPIs** | Tableau Book 14pt bold `#555555` | — | Tableau Book 20pt `#4d60f3` | Tableau Book 12pt bold `#666666` | Tableau Medium 9pt `#666666` | `#787878` |
| **Help Desk** | 24pt `#ffffff` (on dark bg) | 10pt bold `#364781` | 10pt bold `#364781` | 8-9pt `#3d475f` | 8pt `#3d475f` | 8pt `#3d475f` |

### Typography formatting rules

- **Line height**: 1.4-1.5× font size
- **Maximum 3-4 font sizes** per dashboard
- **Bold (600+)** reserved for titles, KPIs, and emphasis only
- **Minimum readable size**: 8px for comparison text, 10px for labels, 12px for body text
- **Sentence case** for all headers (not Title Case)
- **BAN values** should be the largest, boldest text after the dashboard title
- **Comparison text** (vs PM, vs LY) should be the smallest, using muted colors
- **Section separators**: Use `|` character between sections (e.g., "SUMMARY | DETAIL") at 14pt bold with contrasting colors

---

## 5. KPI card and BAN design

### KPI card anatomy

Every KPI card should include:
1. **Metric name** (simple: "Revenue" not "Total Revenue Amount")
2. **BAN (Big Ass Number)** - the primary value
3. **Context** - comparison, trend, or benchmark
4. **Time period** - when optional, show date range

### KPI card dimensions

```
┌──────────────────────────────────────┐
│ Revenue                        📈    │  12-14px, metric name
│                                      │
│     $5.2M                            │  36-48px, BAN (bold)
│                                      │
│  ▲ 8.5% vs last month               │  10-12px, comparison
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔             │  Optional sparkline
└──────────────────────────────────────┘

DIMENSIONS:
├── Card width: 200-300px (minimum 150px)
├── Card height: 100-150px (with sparkline: 150-200px)
├── BAN font size: 36-48px
├── Inner padding: 16-24px
└── Card spacing: 16-24px between cards
```

### KPI formatting rules

**Number formatting:**
```
< 10,000: Show full number (8,547)
10,000 - 999,999: Show as K (125.4K)
1,000,000+: Show as M (2.3M)
1,000,000,000+: Show as B (1.5B)

Always include:
- Currency symbols for money ($, €, £)
- Percentage signs for ratios (8.5%)
- Directional indicators (▲ ▼ or +/-)
```

**Color coding for KPIs:**
- Green (`#198038`): Positive change, goal met
- Red (`#da1e28`): Negative change, below target (use sparingly)
- Neutral blue/gray: When direction is unclear

---

## 6. Chart selection guide

### Decision matrix by analytical goal

| Goal | Best Chart Types | Avoid |
|------|------------------|-------|
| **Compare categories** | Bar chart (horizontal for many items), Column chart | Pie chart (>5 slices) |
| **Show trends over time** | Line chart, Area chart | Bar chart for continuous time |
| **Part-to-whole** | Treemap, Stacked bar, Donut (2-5 parts only) | Pie chart (>5 parts) |
| **Distribution** | Histogram, Box plot | Line chart |
| **Correlation** | Scatter plot | Line chart |
| **Ranking** | Horizontal bar chart, Bump chart | Column chart for many items |
| **Geographic** | Choropleth (rates), Symbol map (totals) | 3D maps |
| **Performance vs target** | Bullet chart, BANs with indicators | Gauges |

### Chart-specific rules

**Bar/Column charts:**
- Always start y-axis at zero
- Use horizontal bars for >7 categories or long labels
- Sort by value (not alphabetically) unless logical order exists
- Maximum 15-20 bars before considering aggregation

**Line charts:**
- Use for continuous data (time series)
- Maximum 5-7 lines before chart becomes unreadable
- Label lines directly at endpoints when possible
- Include zero baseline only if meaningful

**Pie/Donut charts:**
- Maximum 5-6 slices
- Only use when showing parts of 100%
- Order slices by size (largest starting at 12 o'clock)
- Consider alternatives (bar chart, treemap)

---

## 7. Filter and parameter design

### Filter placement patterns

**Top horizontal bar** (recommended for 2-5 global filters):
```
┌─────────────────────────────────────────────────────────┐
│ [Date Range ▼] [Region ▼] [Category ▼]  [Apply] [Clear] │
├─────────────────────────────────────────────────────────┤
│                    DASHBOARD CONTENT                    │
└─────────────────────────────────────────────────────────┘
Height: 40-60px
```

**Left sidebar** (recommended for 5+ filters):
```
┌────────────┬────────────────────────────────────────────┐
│ FILTERS    │                                            │
│            │                                            │
│ Date       │                                            │
│ [▼ 2024  ] │          DASHBOARD CONTENT                 │
│            │                                            │
│ Region     │                                            │
│ [▼ All   ] │                                            │
└────────────┴────────────────────────────────────────────┘
Width: 200-280px
```

### Filter organization order

1. Time-based filters (Year, Quarter, Month)
2. Geographic filters (Region, State, City)
3. Category filters (Product, Segment)
4. Less common filters (under "More Filters" expandable)

### Filter best practices

- **Enable "Show Apply Button"** for multi-select filters (prevents query per click)
- **Use filter actions** instead of quick filters for guided analytics
- **Use "Only Relevant Values" selectively** — appropriate for small filter lists; use "All Values in Database" for large datasets to reduce query overhead
- **Prefer Include over Exclude** filters (better performance)
- **Use continuous date filters** (range/relative) over discrete dates
- **Limit total filters** - each adds database queries

---

## 8. Dashboard actions and interactivity

### Action types and when to use

| Action Type | Trigger | Use Case |
|-------------|---------|----------|
| **Filter** | Select | Click one chart to filter others |
| **Highlight** | Hover | Show related data across views without filtering |
| **URL** | Select/Menu | Link to external resources, documentation |
| **Go to Sheet** | Select | Navigate between dashboards |
| **Parameter** | Select | Dynamic date selection, button controls |
| **Set** | Select | Proportional brushing, drill-down, dynamic grouping |

### Filter action configuration

```
CLEARING SELECTION BEHAVIOR:
├── "Leave the filter" → Keeps last filtered state
├── "Show all values" → Returns to unfiltered state (most common)
└── "Exclude all values" → Hides all data (useful for conditional visibility)
```

### Performance tip for actions

Add the **target field** to your target view's level of detail—enables in-browser filtering instead of database queries.

---

## 9. Performance optimization checklist

### Dashboard design optimizations

```
HIGH IMPACT:
☐ Limit to 2-4 sheets per dashboard (up to 5 for KPI-heavy layouts)
☐ Use Fixed size dashboards (enables server caching)
☐ Enable "Show Apply Button" on filters
☐ Use filter/set actions instead of quick filters
☐ Remove unused worksheets, calculations, data sources

MEDIUM IMPACT:
☐ Same level of detail across dashboard sheets (enables query batching)
☐ Hide unused fields before creating extracts
☐ Use extracts instead of live connections when real-time not required
☐ Avoid COUNTD function when possible (slowest aggregation)
☐ Use Booleans/Integers over Strings/Dates for filtering

LOW IMPACT:
☐ Minimize marks in view (only necessary fields)
☐ Turn off automatic updates while building
☐ Delete custom geocoding if not needed
```

### Data type performance (fastest to slowest)

1. Booleans
2. Integers
3. Floats
4. Strings
5. Dates

### Filter performance order (fastest to slowest)

1. Extract filters (applied at creation)
2. Data source filters (before calculations)
3. Context filters (pre-compute)
4. Dimension filters
5. Measure filters
6. Table calculation filters

---

## 10. Accessibility requirements

### WCAG contrast ratios (required)

| Element | Minimum Ratio | Enhanced (AAA) |
|---------|---------------|----------------|
| Normal text (<18pt) | **4.5:1** | 7:1 |
| Large text (≥18pt or 14pt bold) | **3:1** | 4.5:1 |
| Non-text (charts, UI elements) | **3:1** | — |

### Accessibility checklist

```
☐ Text contrast ratio ≥ 4.5:1 against background
☐ Chart elements contrast ratio ≥ 3:1
☐ No red-green only color encoding
☐ Include shape or pattern with color
☐ Provide text alternatives for key insights
☐ Add objects in logical reading order (affects screen reader)
☐ Use descriptive titles and subtitles
☐ Test with color blindness simulators
```

---

## 11. Device-specific layouts

### Desktop layout (default)

- **Size**: 1300×900 to 1600×900px
- **Full interactivity** with filters and actions
- **All visualizations** visible

### Tablet layout

- **Orientation**: Prefer landscape
- **Size**: 1024×768px typical
- **Simplify**: Remove some secondary visualizations
- **Touch-friendly**: Larger filter controls, more padding

### Phone layout

- **Orientation**: Portrait (vertical scroll)
- **Size**: Fit Width with ~1300px height
- **Aggressive simplification**:
  - Focus on 1-2 key KPIs
  - Maximum 2 visualizations
  - Simplified/removed filters
  - Shortened titles
  - Add safe touch zones (padding/blanks for scrolling)
- **Auto-generate option**: Follows z-reading pattern

### Mobile-specific actions

```
URL Actions for mobile:
- Phone call: tel:+1-555-123-4567
- SMS: sms:+1-555-123-4567
```

---

## 12. Tooltip design

### Tooltip structure

```
┌─────────────────────────────────┐
│ **Region: West**                │  Bold key identifier
│ **State: California**           │
│                                 │
│ Sales: $2.4M                    │  Primary metric
│ Profit: $340K (14.2%)           │  Secondary metrics
│ vs Target: ▲ +$50K              │  Comparison
└─────────────────────────────────┘
```

### Tooltip rules

- Remove default "Automatic" tooltip content
- Keep to 3-5 lines maximum
- Bold key identifiers (dimensions)
- Include comparison/context
- Use sentence-style formatting
- **Disable tooltips on KPI BANs** (obstruct the number)
- Consider Viz-in-Tooltip for drill-down detail

---

## 13. Header and navigation design

### Dashboard header structure

```
┌─────────────────────────────────────────────────────────────────┐
│ [LOGO 32-40px]  [DASHBOARD TITLE 20-24px]      [NAV] [UPDATED]  │
│                 [Subtitle 12-14px]              [FILTERS]       │
└─────────────────────────────────────────────────────────────────┘
Height: 50-80px (up to 120px with filters)
```

### Navigation patterns

**Tab navigation** (top of dashboard):
- Maximum 5-7 tabs
- Active tab: bold, underlined, or highlighted
- Consistent position across all dashboards

**Button navigation**:
- Clear labeling: "View Details" not "Details"
- Visual feedback on hover/click
- Use Navigation object or Go to Sheet actions

**Sidebar navigation** (left side):
- Width: 200-280px expanded, 60-80px collapsed
- Icons + labels for clarity
- Group related items with dividers

---

## 14. Legend and annotation placement

### Legend positioning decision

| Position | When to Use |
|----------|-------------|
| Below chart | Default for most visualizations |
| Right of chart | Sequential/diverging color scales |
| Integrated in title | Color-coded titles act as legend |
| Direct labels | **Preferred when possible** (2-8 categories) |

### Direct labeling rules

- Label line chart endpoints instead of legend
- Label largest bars in bar charts (establish pattern)
- Label pie/donut slices directly
- Remove legends when direct labels are present

### Annotation guidelines

- Use sparingly—highlight only key insights
- Position close to relevant data point
- Don't obscure underlying data
- Consistent styling (callout boxes, arrows)

---

## 15. Common dashboard templates

### Executive summary template

```
┌─────────────────────────────────────────────────────────────────┐
│ [LOGO]  [Dashboard Title]                    [Date] [Filters]   │  60px
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│ │ KPI 1    │ │ KPI 2    │ │ KPI 3    │ │ KPI 4    │            │  120px
│ │ $5.2M ▲  │ │ 12.3K ▼  │ │ 8.5%  ▲  │ │ 94.2  —  │            │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
├────────────────────────────────────────┬────────────────────────┤
│                                        │                        │
│     [PRIMARY TREND/MAP]                │  [BREAKDOWN CHART]     │
│          ~60% width                    │      ~40% width        │  ~400px
│                                        │                        │
├────────────────────────────────────────┴────────────────────────┤
│     [DETAIL TABLE OR SUPPORTING VISUALIZATION]                  │  ~220px
└─────────────────────────────────────────────────────────────────┘
Total: 1300 × 900px
```

### Analytical deep-dive template

```
┌────────────────────────────────────────────────────────────────┐
│ [HEADER: Title, Filters, Navigation]                           │  60px
├──────────────┬─────────────────────────────────────────────────┤
│              │  [KPI 1] [KPI 2] [KPI 3]                        │  80px
│   FILTER     ├─────────────────────────────────────────────────┤
│   SIDEBAR    │                                                 │
│              │     [PRIMARY VISUALIZATION]                     │
│   200-250px  │                                                 │  ~400px
│              │                                                 │
│              ├──────────────────────┬──────────────────────────┤
│              │  [SECONDARY CHART]   │  [SECONDARY CHART]       │  ~260px
└──────────────┴──────────────────────┴──────────────────────────┘
Total: 1400 × 800px
```

---

## 16. Design checklist for review

### Before publishing

```
LAYOUT & SIZING:
☐ Dashboard sized appropriately for target display
☐ Device-specific layouts created if mobile/tablet needed
☐ Containers named descriptively
☐ Consistent padding and spacing

VISUAL HIERARCHY:
☐ Most important content in upper-left
☐ KPIs prominently displayed with context
☐ Clear visual flow (Z or F pattern)
☐ Maximum 2-4 sheets per dashboard (up to 5 for KPI-heavy layouts)

COLOR & TYPOGRAPHY:
☐ Maximum 6-10 colors used
☐ Color palette is colorblind-safe
☐ Font hierarchy established (3-4 sizes max)
☐ Text contrast meets WCAG 4.5:1

INTERACTIVITY:
☐ Filters have "Apply" button enabled
☐ Actions configured appropriately
☐ Tooltips customized (not default)
☐ Navigation is intuitive

PERFORMANCE:
☐ Dashboard loads in under 5 seconds
☐ Unused fields hidden/removed
☐ Appropriate filter types selected
☐ Tested at actual viewing size

ACCESSIBILITY:
☐ All text meets contrast requirements
☐ No reliance on color alone
☐ Titles and subtitles provide context
☐ Objects added in logical reading order
```

---

## 17. Clean design techniques (learned from reference dashboards)

### Card-based layout

The cleanest dashboards use white cards on a subtle gray background:

```xml
<!-- Card zone styling -->
<zone-style>
  <format attr='border-color' value='#e8f0f7' />
  <format attr='border-style' value='solid' />
  <format attr='border-width' value='1' />
  <format attr='margin' value='4' />
  <format attr='padding' value='10' />
  <format attr='background-color' value='#ffffff' />
</zone-style>
```

**Key values by dashboard:**

| Dashboard | Border color | Border width | Margin | Padding | Background |
|-----------|-------------|--------------|--------|---------|------------|
| Google Ads | `#e8f0f7` | 1px | 4px | 10px | `#ffffff` |
| Global Software | `#a3bdf1` | 1px | — | 20px L/R, 15px T | `#ffffff` |
| Dynamic Zone KPIs | `#dbdffd` | 1px | 8px | 8px | `#ffffff` |
| Help Desk | none | 0 | 15px | 20px | `#ffffff` |

### Removing visual clutter

```xml
<!-- Hide gridlines -->
<format attr='stroke-size' value='0' />
<format attr='line-visibility' scope='cols' value='off' />
<format attr='line-visibility' scope='rows' value='off' />

<!-- Hide borders on worksheets -->
<format attr='border-style' value='none' />
<format attr='border-width' value='0' />

<!-- Transparent worksheet background -->
<format attr='background-color' value='#00000000' />
```

### Info button with documentation panel

Every dashboard should include an info button (i icon) that toggles a documentation panel explaining KPI definitions, data sources, and usage instructions. This pattern is used in the Global Software Retail Analytics dashboard with `icons8-info-96` PNG icons.

**Info panel structure:**
- White background (`#ffffff`) with 1px `#c0c0c0` border
- 30px padding for comfortable reading
- Title: 12pt bold
- Body: 10pt regular
- Sections: "How to Use", "Indicator Guide", "Data Sources"

### Navigation sidebar best practices

| Element | Google Ads (none) | Global Software | Help Desk |
|---------|------------------|-----------------|-----------|
| Sidebar width | — | 240px fixed | ~125px header |
| Nav items | Inline tabs | Image buttons | Image buttons |
| Active indicator | `#3c8bd9` text color | 5px `#6279b8` left bar | 3px white bottom border |
| Background | — | `#ffffff` | `#3d475f` (dark) |
| Icons | — | Custom PNGs per page | Overview/Table/Settings PNGs |
| Navigation action | — | `tabdoc:goto-sheet` | `tabdoc:goto-sheet` |

### KPI comparison indicator patterns

**Pattern 1 — Split positive/negative fields (Google Ads):**
- Separate calculated fields for positive % (green) and negative % (red)
- `IF SIGN([delta]) = 1 THEN "+" + STR(ROUND([delta], 1)) + "%" ELSE "" END`
- `IF SIGN([delta]) = -1 THEN STR(ROUND([delta], 1)) + "%" ELSE "" END`
- Each displayed with its own color in `<run>` elements

**Pattern 2 — Arrow symbols with color (Global Software):**
- Single % change field with conditional color
- Arrow: ▲ (positive, `#59a14f`), ▼ (negative, `#e15759`)
- Format: `<run fontcolor='#59a14f'><![CDATA[<[positive_field]>]]></run>`

**Pattern 3 — Shape-driven arrows (Google Ads):**
- `SIGN()` of delta drives a shape encoding (`Arrows/1-8.png`)
- `<format attr='shape' value='Arrows/1-8.png' />`

**Pattern 4 — Trend arrows with icons (Help Desk):**
- Custom arrow shapes: `My Arrows/Up.png`, `Same.png`, `Down.png`
- Color: `#819cff` (up), `#9de1e5` (same), `#ff6788` (down)

### Image assets checklist

When creating a dashboard with images, include:
- [ ] Navigation icons (one per dashboard page)
- [ ] KPI category icons (one per metric)
- [ ] Info button icon (`icons8-info-96.png` or similar)
- [ ] Logo/branding image
- [ ] Background image (optional, for decorative design)
- [ ] Close/X button icon (for dismissable panels)
- [ ] Social/export icons (GitHub, LinkedIn, PDF, image export)

---

## Sources and references

This guide synthesizes best practices from:
- Tableau Desktop Help Documentation (help.tableau.com)
- Tableau Blueprint Visual Best Practices
- Dub Dub Data: "10 Best Practices for Tableau"
- IBM Carbon Design System (color palettes)
- WCAG 2.1 Accessibility Guidelines
- Edward Tufte's data visualization principles
- Stephen Few's dashboard design methodology
- Designing Efficient Workbooks whitepaper (Tableau)
