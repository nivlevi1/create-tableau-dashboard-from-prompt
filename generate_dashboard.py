#!/usr/bin/env python3
"""
NIS Forex Exchange Rate Dashboard Generator
Run from project root: python generate_dashboard.py
Output: nis_forex_dashboard.twb
"""

import xml.etree.ElementTree as ET
import uuid
from datetime import date, timedelta
from pathlib import Path

# ── IDs ───────────────────────────────────────────────────────────────────────
DS_NAME    = 'textscan.nisexchange001'
DS_CAPTION = 'NIS Exchange Rates'
CSV_DIR    = str(Path('src/NIS_Exchange_Rates.csv').resolve().parent).replace('\\', '/')
CSV_FILE   = 'NIS_Exchange_Rates.csv'

P_CURRENCY = '[Parameter 1]'
P_GRANUL   = '[Parameter 2]'
P_START    = '[Parameter 3]'
P_END      = '[Parameter 4]'

# Calculated field internal names (19-digit pattern per §3 of learnings)
C_SEL_RATE = '[Calculation_1000000000000000001]'  # Selected Rate (CASE on currency)
C_SEL_DATE = '[Calculation_1000000000000000002]'  # Selected Date (Dynamic)
C_DATE_IN  = '[Calculation_1000000000000000003]'  # Date In Range (boolean filter)
C_PERIOD_C = '[Calculation_1000000000000000004]'  # Period Change % (period-over-period table calc)
C_MONTH_NM = '[Calculation_1000000000000000005]'  # Month Name
C_MONTH_NO = '[Calculation_1000000000000000006]'  # Month Number (sort key)
C_DOW_NM   = '[Calculation_1000000000000000007]'  # Day of Week Name
C_DOW_NO   = '[Calculation_1000000000000000008]'  # Day Number (sort key)
C_DATE_LBL = '[Calculation_1000000000000000009]'  # Period Label (formatted string for axis)
C_CUM_CHG  = '[Calculation_0697156532551683]'      # Cumulative % Change (from first period)

TODAY      = date.today()
START_DATE = TODAY - timedelta(days=365)
DASH_NAME  = 'NIS Forex Dashboard'

CURRENCIES = ['USD', 'GBP', 'JPY_100', 'EUR', 'CHF']
SHEET_NAMES = [
    'KPI Avg Rate', 'KPI Period High', 'KPI Period Low', 'KPI Data Points',
    'Main Trend Line', 'Monthly Seasonality', 'Day-of-Week Pattern',
    'Volatility Line', 'Period Change Bars', 'Multi-Currency Comparison',
]

# ── XML helpers ───────────────────────────────────────────────────────────────

def new_uuid():
    return '{' + str(uuid.uuid4()).upper() + '}'


def sub(parent, tag, text=None, **attrs):
    e = ET.SubElement(parent, tag)
    for k, v in attrs.items():
        e.set(k, v)
    if text is not None:
        e.text = text
    return e


def fmt(style_rule, attr, value):
    f = ET.SubElement(style_rule, 'format')
    f.set('attr', attr)
    f.set('value', value)


def col(parent, name, caption, datatype, role, typ,
        formula=None, default_format=None, **extra):
    e = ET.SubElement(parent, 'column')
    e.set('caption', caption)
    e.set('datatype', datatype)
    e.set('name', name)
    e.set('role', role)
    e.set('type', typ)
    if default_format:
        e.set('default-format', default_format)
    for k, v in extra.items():
        e.set(k, v)
    if formula is not None:
        c = ET.SubElement(e, 'calculation')
        c.set('class', 'tableau')
        c.set('formula', formula)
    return e


def dep_col(deps, name, caption, datatype, role, typ):
    """Add column to datasource-dependencies."""
    e = ET.SubElement(deps, 'column')
    e.set('caption', caption)
    e.set('datatype', datatype)
    e.set('name', name)
    e.set('role', role)
    e.set('type', typ)
    return e


def dep_ci(deps, column_name, derivation, inst_name, typ):
    """Add column-instance to datasource-dependencies."""
    e = ET.SubElement(deps, 'column-instance')
    e.set('column', column_name)
    e.set('derivation', derivation)
    e.set('name', inst_name)
    e.set('pivot', 'key')
    e.set('type', typ)
    return e


def fq(inst):
    """Fully-qualified shelf reference: [DS_NAME].[inst]"""
    return f'[{DS_NAME}].{inst}'


# ── Parameters datasource ─────────────────────────────────────────────────────

def build_params_ds():
    ds = ET.Element('datasource')
    ds.set('hasconnection', 'false')
    ds.set('inline', 'true')
    ds.set('name', 'Parameters')
    ds.set('version', '18.1')
    sub(ds, 'aliases', enabled='yes')

    # Currency Selector
    p1 = ET.SubElement(ds, 'column')
    p1.set('caption', 'Currency Selector')
    p1.set('datatype', 'string')
    p1.set('name', P_CURRENCY)
    p1.set('param-domain-type', 'list')
    p1.set('role', 'measure')
    p1.set('type', 'nominal')
    p1.set('value', '"USD"')
    c1 = ET.SubElement(p1, 'calculation')
    c1.set('class', 'tableau')
    c1.set('formula', '"USD"')
    mems = ET.SubElement(p1, 'members')
    for cur in CURRENCIES:
        m = ET.SubElement(mems, 'member')
        m.set('value', f'"{cur}"')

    # Time Granularity — default Day (matches validated workbook)
    p2 = ET.SubElement(ds, 'column')
    p2.set('caption', 'Time Granularity')
    p2.set('datatype', 'string')
    p2.set('name', P_GRANUL)
    p2.set('param-domain-type', 'list')
    p2.set('role', 'measure')
    p2.set('type', 'nominal')
    p2.set('value', '"Day"')
    c2 = ET.SubElement(p2, 'calculation')
    c2.set('class', 'tableau')
    c2.set('formula', '"Day"')
    mems2 = ET.SubElement(p2, 'members')
    for g in ['Day', 'Week', 'Month', 'Quarter', 'Year']:
        m = ET.SubElement(mems2, 'member')
        m.set('value', f'"{g}"')

    # Start Date / End Date
    for name, caption, default in [
        (P_START, 'Start Date', f'#{START_DATE}#'),
        (P_END,   'End Date',   f'#{TODAY}#'),
    ]:
        p = ET.SubElement(ds, 'column')
        p.set('caption', caption)
        p.set('datatype', 'date')
        p.set('name', name)
        p.set('param-domain-type', 'any')
        p.set('role', 'measure')
        p.set('type', 'quantitative')
        p.set('value', default)
        c = ET.SubElement(p, 'calculation')
        c.set('class', 'tableau')
        c.set('formula', default)

    return ds


# ── Data datasource ───────────────────────────────────────────────────────────

def build_data_ds():
    ds = ET.Element('datasource')
    ds.set('caption', DS_CAPTION)
    ds.set('inline', 'true')
    ds.set('name', DS_NAME)
    ds.set('version', '18.1')

    conn = ET.SubElement(ds, 'connection')
    for k, v in [
        ('class', 'textscan'), ('cleaning', 'no'), ('compat', 'no'),
        ('dataRefreshTime', ''), ('directory', CSV_DIR), ('filename', CSV_FILE),
        ('filetype', 'csv'), ('locale', 'en_US'), ('protocol', 'csv-file'),
        ('validate', 'no'),
    ]:
        conn.set(k, v)

    csv_tbl = 'NIS_Exchange_Rates#csv'
    rel = sub(conn, 'relation', name=csv_tbl, table=f'[{csv_tbl}]', type='table')
    cols_e = sub(rel, 'columns', header='yes', outcome='6')
    for i, (cname, dtype) in enumerate([
        ('Date', 'date'), ('USD', 'real'), ('GBP', 'real'), ('JPY_100', 'real'),
        ('EUR', 'real'), ('CHF', 'real'), ('updated_at', 'string'),
    ]):
        c = ET.SubElement(cols_e, 'column')
        c.set('datatype', dtype)
        c.set('name', cname)
        c.set('ordinal', str(i))

    # aliases MUST come before <column> elements
    sub(ds, 'aliases', enabled='yes')

    # Physical columns
    col(ds, '[Date]',       'Date',       'date',   'dimension', 'ordinal')
    col(ds, '[USD]',        'USD',        'real',   'measure',   'quantitative')
    col(ds, '[GBP]',        'GBP',        'real',   'measure',   'quantitative')
    col(ds, '[JPY_100]',    'JPY/100',    'real',   'measure',   'quantitative')
    col(ds, '[EUR]',        'EUR',        'real',   'measure',   'quantitative')
    col(ds, '[CHF]',        'CHF',        'real',   'measure',   'quantitative')
    col(ds, '[updated_at]', 'Updated At', 'string', 'dimension', 'nominal', hidden='true')

    # ── Calculated fields ────────────────────────────────────────────────────
    sr = C_SEL_RATE[1:-1]

    # Selected Rate — driven by Currency Selector parameter
    col(ds, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative',
        formula=(
            'CASE [Parameters].[Parameter 1] '
            'WHEN "USD" THEN [USD] WHEN "GBP" THEN [GBP] '
            'WHEN "JPY_100" THEN [JPY_100] WHEN "EUR" THEN [EUR] '
            'WHEN "CHF" THEN [CHF] END'
        ))

    # Selected Date (Dynamic) — string label driven by Time Granularity parameter
    col(ds, C_SEL_DATE, 'Selected Date (Dynamic)', 'string', 'dimension', 'nominal',
        formula=(
            'CASE [Parameters].[Parameter 2] '
            'WHEN "Day" THEN STR(YEAR([Date])) + "-" + RIGHT("0" + STR(MONTH([Date])),2) + "-" + RIGHT("0" + STR(DAY([Date])),2) '
            'WHEN "Week" THEN STR(YEAR([Date])) + "-W" + RIGHT("0" + STR(DATEPART(\'week\',[Date])),2) '
            'WHEN "Month" THEN STR(YEAR([Date])) + "-" + RIGHT("0" + STR(MONTH([Date])),2) '
            'WHEN "Quarter" THEN STR(YEAR([Date])) + "-Q" + STR(DATEPART(\'quarter\',[Date])) '
            'WHEN "Year" THEN STR(YEAR([Date])) '
            'END'
        ))

    # Date In Range — boolean filter field
    col(ds, C_DATE_IN, 'Date In Range', 'boolean', 'dimension', 'nominal',
        formula='[Date] >= [Parameters].[Parameter 3] AND [Date] <= [Parameters].[Parameter 4]')

    # Period Change % — period-over-period table calculation
    col(ds, C_PERIOD_C, 'Period Change %', 'real', 'measure', 'quantitative',
        default_format='p1%',
        formula=(
            f'ZN((LOOKUP(AVG([{sr}]), 0) - LOOKUP(AVG([{sr}]), -1)) '
            f'/ ABS(LOOKUP(AVG([{sr}]), -1)))'
        ))

    # Cumulative % Change — change from the very first period (used by Volatility Line)
    col(ds, C_CUM_CHG, 'Cumulative % Change', 'real', 'measure', 'quantitative',
        formula=(
            f'ZN(\n'
            f'    (AVG([{sr}]) - LOOKUP(AVG([{sr}]), FIRST()))\n'
            f'    / ABS(LOOKUP(AVG([{sr}]), FIRST()))\n'
            f')'
        ))

    # Date-part helpers for seasonality sheets
    col(ds, C_MONTH_NM, 'Month Name',   'string',  'dimension', 'nominal',
        formula="DATENAME('month', [Date])")
    col(ds, C_MONTH_NO, 'Month Number', 'integer', 'dimension', 'ordinal',
        formula='MONTH([Date])')
    col(ds, C_DOW_NM,   'Day of Week',  'string',  'dimension', 'nominal',
        formula="DATENAME('weekday', [Date])")
    col(ds, C_DOW_NO,   'Day Number',   'integer', 'dimension', 'ordinal',
        formula="DATEPART('weekday', [Date])")

    # Period Label — alternate MM-YYYY / DD/MM/YYYY style, references [Date] directly
    lbl_formula = (
        f'CASE [Parameters].{P_GRANUL} '
        f'WHEN "Year" THEN STR(YEAR([Date])) '
        f'WHEN "Quarter" THEN "Q" + STR(DATEPART(\'quarter\',[Date])) + "-" + STR(YEAR([Date])) '
        f'WHEN "Month" THEN RIGHT("0" + STR(MONTH([Date])), 2) + "-" + STR(YEAR([Date])) '
        f'WHEN "Week" THEN "W" + RIGHT("0" + STR(DATEPART(\'week\',[Date])), 2) + "-" + STR(YEAR([Date])) '
        f'WHEN "Day" THEN STR(MONTH([Date])) + "/" + STR(DAY([Date])) + "/" + STR(YEAR([Date])) '
        f'END'
    )
    col(ds, C_DATE_LBL, 'Period Label', 'string', 'dimension', 'nominal', formula=lbl_formula)

    return ds


# ── Worksheet scaffolding helpers ─────────────────────────────────────────────

def ws_start(name, title=None):
    """Return (ws, table). Adds layout-options title."""
    ws = ET.Element('worksheet', name=name)
    lo = ET.SubElement(ws, 'layout-options')
    t  = ET.SubElement(lo, 'title')
    ft = ET.SubElement(t, 'formatted-text')
    r  = ET.SubElement(ft, 'run')
    r.set('fontname', 'Tableau Bold')
    r.set('fontsize', '11')
    r.text = title or name
    table = ET.SubElement(ws, 'table')
    return ws, table


def make_view(table):
    """Create <view> with datasource refs, return (view, deps)."""
    view = ET.SubElement(table, 'view')
    dss  = ET.SubElement(view, 'datasources')
    sub(dss, 'datasource', caption=DS_CAPTION, name=DS_NAME)
    sub(dss, 'datasource', name='Parameters')
    deps = ET.SubElement(view, 'datasource-dependencies', datasource=DS_NAME)
    return view, deps


def add_date_filter(view, deps):
    """Add the Date In Range boolean filter."""
    inst = f'[none:{C_DATE_IN[1:-1]}:nk]'
    dep_col(deps, C_DATE_IN, 'Date In Range', 'boolean', 'dimension', 'nominal')
    dep_ci(deps, C_DATE_IN, 'None', inst, 'nominal')
    f = ET.SubElement(view, 'filter')
    f.set('class', 'categorical')
    f.set('column', fq(inst))
    gf = ET.SubElement(f, 'groupfilter')
    gf.set('function', 'member')
    gf.set('level', inst)
    gf.set('member', 'true')


def clean_style(table, mark_labels=False):
    """Standard no-gridline, no-axis style."""
    style = ET.SubElement(table, 'style')
    sr = ET.SubElement(style, 'style-rule'); sr.set('element', 'axis')
    fmt(sr, 'stroke-size', '0')
    fmt(sr, 'line-visibility', 'off')
    sr = ET.SubElement(style, 'style-rule'); sr.set('element', 'axis-title')
    fmt(sr, 'display', 'off')
    sr = ET.SubElement(style, 'style-rule'); sr.set('element', 'gridline')
    fmt(sr, 'line-visibility', 'off')
    sr = ET.SubElement(style, 'style-rule'); sr.set('element', 'refline')
    fmt(sr, 'line-visibility', 'off')
    if mark_labels:
        sr = ET.SubElement(style, 'style-rule'); sr.set('element', 'mark')
        fmt(sr, 'mark-labels-show', 'true')
        fmt(sr, 'mark-labels-cull', 'true')
    return style


def make_pane(table, mark_class):
    """Add <panes> block with given mark class."""
    panes = ET.SubElement(table, 'panes')
    pane  = ET.SubElement(panes, 'pane')
    pane.set('selection-relaxation-option', 'selection-relaxation-allow')
    v = ET.SubElement(pane, 'view')
    sub(v, 'breakdown', value='auto')
    sub(pane, 'mark', **{'class': mark_class})
    return pane


def add_encoding(pane, enc_type, col_ref):
    encs = pane.find('encodings')
    if encs is None:
        encs = ET.SubElement(pane, 'encodings')
    sub(encs, enc_type, column=col_ref)


def finish_ws(ws, table, rows='', cols=''):
    """Add rows/cols and simple-id. rows/cols MUST be on <table>, not <view>."""
    sub(table, 'rows', text=rows)
    sub(table, 'cols', text=cols)
    sub(ws, 'simple-id', uuid=new_uuid())


def add_bar_mark_style(pane):
    """Add the standard bar mark color: #d0e4f9 fill + #006ce0 stroke."""
    style = ET.SubElement(pane, 'style')
    sr = ET.SubElement(style, 'style-rule')
    sr.set('element', 'mark')
    fmt(sr, 'mark-color', '#d0e4f9')
    fmt(sr, 'mark-transparency', '255')
    fmt(sr, 'has-stroke', 'true')
    fmt(sr, 'stroke-color', '#006ce0')


def add_line_mark_style(pane):
    """Add the standard line mark color: #006ce0."""
    style = ET.SubElement(pane, 'style')
    sr = ET.SubElement(style, 'style-rule')
    sr.set('element', 'mark')
    fmt(sr, 'mark-color', '#006ce0')


def add_kpi_customized_label(pane, inst_ref, shekel=True, value_color=None):
    """
    Add <customized-label> to a KPI text pane.
    inst_ref: fully-qualified column-instance string (e.g. '[DS].[avg:X:qk]')
    shekel: whether to append ₪ after the value
    value_color: optional hex color for the value run (e.g. '#006ce0')
    """
    label = ET.SubElement(pane, 'customized-label')
    ft = ET.SubElement(label, 'formatted-text')

    # Value reference: use three runs (<, field_ref, >) to avoid CDATA
    for part in ['<', inst_ref, '>']:
        run = ET.SubElement(ft, 'run')
        run.set('bold', 'true')
        run.set('fontsize', '20')
        if value_color:
            run.set('fontcolor', value_color)
        run.text = part

    # ₪ symbol in smaller Benton Sans Book font
    if shekel:
        shekel_run = ET.SubElement(ft, 'run')
        shekel_run.set('fontname', 'Benton Sans Book')
        shekel_run.set('fontsize', '10')
        if value_color:
            shekel_run.set('fontcolor', value_color)
        shekel_run.text = '₪'

    # Center alignment
    pane_style = ET.SubElement(pane, 'style')
    sr = ET.SubElement(pane_style, 'style-rule')
    sr.set('element', 'cell')
    fmt(sr, 'text-align', 'center')


# ── KPI text-mark worksheets ──────────────────────────────────────────────────

def build_kpi_avg_rate():
    sr = C_SEL_RATE[1:-1]
    inst_name = f'[avg:{sr}:qk]'

    ws, table = ws_start('KPI Avg Rate', 'Avg Exchange Rate')
    view, deps = make_view(table)

    dep_col(deps, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_SEL_RATE, 'Avg', inst_name, 'quantitative')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    style = clean_style(table, mark_labels=True)
    # KPI value color
    sr_cell = ET.SubElement(style, 'style-rule')
    sr_cell.set('element', 'cell')
    fmt(sr_cell, 'color', '#006ce0')
    # Transparent background
    sr_tbl = ET.SubElement(style, 'style-rule')
    sr_tbl.set('element', 'table')
    fmt(sr_tbl, 'background-color', '#00000000')

    panes = ET.SubElement(table, 'panes')
    pane = ET.SubElement(panes, 'pane')
    pane.set('selection-relaxation-option', 'selection-relaxation-allow')
    v = ET.SubElement(pane, 'view')
    sub(v, 'breakdown', value='auto')
    sub(pane, 'mark', **{'class': 'Text'})
    encs = ET.SubElement(pane, 'encodings')
    sub(encs, 'text', column=fq(inst_name))
    add_kpi_customized_label(pane, inst_name, shekel=True, value_color=None)

    finish_ws(ws, table)
    return ws


def build_kpi_period_high():
    sr = C_SEL_RATE[1:-1]
    inst_name = f'[max:{sr}:qk]'

    ws, table = ws_start('KPI Period High', 'Period High')
    view, deps = make_view(table)

    dep_col(deps, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_SEL_RATE, 'Max', inst_name, 'quantitative')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    style = clean_style(table, mark_labels=True)
    sr_tbl = ET.SubElement(style, 'style-rule')
    sr_tbl.set('element', 'table')
    fmt(sr_tbl, 'background-color', '#00000000')

    panes = ET.SubElement(table, 'panes')
    pane = ET.SubElement(panes, 'pane')
    pane.set('selection-relaxation-option', 'selection-relaxation-allow')
    v = ET.SubElement(pane, 'view')
    sub(v, 'breakdown', value='auto')
    sub(pane, 'mark', **{'class': 'Text'})
    encs = ET.SubElement(pane, 'encodings')
    sub(encs, 'text', column=fq(inst_name))
    add_kpi_customized_label(pane, inst_name, shekel=True, value_color='#006ce0')

    finish_ws(ws, table)
    return ws


def build_kpi_period_low():
    sr = C_SEL_RATE[1:-1]
    inst_name = f'[min:{sr}:qk]'

    ws, table = ws_start('KPI Period Low', 'Period Low')
    view, deps = make_view(table)

    dep_col(deps, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_SEL_RATE, 'Min', inst_name, 'quantitative')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    style = clean_style(table, mark_labels=True)
    sr_tbl = ET.SubElement(style, 'style-rule')
    sr_tbl.set('element', 'table')
    fmt(sr_tbl, 'background-color', '#00000000')

    panes = ET.SubElement(table, 'panes')
    pane = ET.SubElement(panes, 'pane')
    pane.set('selection-relaxation-option', 'selection-relaxation-allow')
    v = ET.SubElement(pane, 'view')
    sub(v, 'breakdown', value='auto')
    sub(pane, 'mark', **{'class': 'Text'})
    encs = ET.SubElement(pane, 'encodings')
    sub(encs, 'text', column=fq(inst_name))
    add_kpi_customized_label(pane, inst_name, shekel=True, value_color='#006ce0')

    finish_ws(ws, table)
    return ws


def build_kpi_data_points():
    inst_name = '[cnt:Date:qk]'

    ws, table = ws_start('KPI Data Points', 'Trading Days')
    view, deps = make_view(table)

    dep_col(deps, '[Date]', 'Date', 'date', 'dimension', 'ordinal')
    dep_ci(deps, '[Date]', 'Count', inst_name, 'quantitative')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    style = clean_style(table, mark_labels=True)
    sr_cell = ET.SubElement(style, 'style-rule')
    sr_cell.set('element', 'cell')
    fmt(sr_cell, 'color', '#006ce0')
    sr_tbl = ET.SubElement(style, 'style-rule')
    sr_tbl.set('element', 'table')
    fmt(sr_tbl, 'background-color', '#00000000')

    panes = ET.SubElement(table, 'panes')
    pane = ET.SubElement(panes, 'pane')
    pane.set('selection-relaxation-option', 'selection-relaxation-allow')
    v = ET.SubElement(pane, 'view')
    sub(v, 'breakdown', value='auto')
    sub(pane, 'mark', **{'class': 'Text'})
    encs = ET.SubElement(pane, 'encodings')
    sub(encs, 'text', column=fq(inst_name))
    add_kpi_customized_label(pane, inst_name, shekel=False, value_color=None)

    finish_ws(ws, table)
    return ws


# ── Main Trend Line ───────────────────────────────────────────────────────────
# Dual-axis: thin line + thick line on left axis, area fill on synchronized right axis.

def build_main_trend():
    ws, table = ws_start('Main Trend Line', 'Main Trend Line')
    view, deps = make_view(table)

    sr  = C_SEL_RATE[1:-1]
    sd  = C_SEL_DATE[1:-1]
    sr_inst = f'[avg:{sr}:qk]'
    sd_inst = f'[none:{sd}:nk]'

    dep_col(deps, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_SEL_RATE, 'Avg', sr_inst, 'quantitative')
    dep_col(deps, C_SEL_DATE, 'Selected Date (Dynamic)', 'string', 'dimension', 'nominal')
    dep_ci(deps, C_SEL_DATE, 'None', sd_inst, 'nominal')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    clean_style(table)

    # Three panes for dual-axis line + area effect
    panes = ET.SubElement(table, 'panes')

    # Pane 0: thin line (left axis, first instance)
    p0 = ET.SubElement(panes, 'pane')
    p0.set('selection-relaxation-option', 'selection-relaxation-allow')
    v0 = ET.SubElement(p0, 'view'); sub(v0, 'breakdown', value='auto')
    sub(p0, 'mark', **{'class': 'Line'})
    sub(p0, 'mark-sizing', **{'mark-sizing-setting': 'marks-scaling-off'})
    s0 = ET.SubElement(p0, 'style')
    sr0 = ET.SubElement(s0, 'style-rule'); sr0.set('element', 'mark')
    fmt(sr0, 'mark-color', '#006ce0')

    # Pane 1: thick line (left axis, second instance — gives the bold trend line)
    p1 = ET.SubElement(panes, 'pane')
    p1.set('id', '1')
    p1.set('selection-relaxation-option', 'selection-relaxation-allow')
    p1.set('y-axis-name', fq(sr_inst))
    v1 = ET.SubElement(p1, 'view'); sub(v1, 'breakdown', value='auto')
    sub(p1, 'mark', **{'class': 'Line'})
    sub(p1, 'mark-sizing', **{'mark-sizing-setting': 'marks-scaling-off'})
    s1 = ET.SubElement(p1, 'style')
    sr1 = ET.SubElement(s1, 'style-rule'); sr1.set('element', 'mark')
    fmt(sr1, 'mark-color', '#006ce0')

    # Pane 2: area fill (synchronized right axis)
    p2 = ET.SubElement(panes, 'pane')
    p2.set('id', '2')
    p2.set('selection-relaxation-option', 'selection-relaxation-allow')
    p2.set('y-axis-name', fq(sr_inst))
    p2.set('y-index', '1')
    v2 = ET.SubElement(p2, 'view'); sub(v2, 'breakdown', value='auto')
    sub(p2, 'mark', **{'class': 'Area'})
    sub(p2, 'mark-sizing', **{'mark-sizing-setting': 'marks-scaling-off'})
    s2 = ET.SubElement(p2, 'style')
    sr2 = ET.SubElement(s2, 'style-rule'); sr2.set('element', 'mark')
    fmt(sr2, 'mark-color', '#d0e4f9')
    fmt(sr2, 'mark-transparency', '255')

    # Dual-axis rows: same measure twice creates two synchronized axes
    finish_ws(ws, table,
              rows=f'({fq(sr_inst)} + {fq(sr_inst)})',
              cols=fq(sd_inst))
    return ws


# ── Monthly Seasonality ───────────────────────────────────────────────────────

def build_monthly_seasonality():
    ws, table = ws_start('Monthly Seasonality', 'Monthly Seasonality')
    view, deps = make_view(table)

    sr    = C_SEL_RATE[1:-1]
    mn    = C_MONTH_NM[1:-1]
    sr_inst = f'[avg:{sr}:qk]'
    mn_inst = f'[none:{mn}:nk]'

    dep_col(deps, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_SEL_RATE, 'Avg', sr_inst, 'quantitative')
    dep_col(deps, C_MONTH_NM, 'Month Name', 'string', 'dimension', 'nominal')
    dep_ci(deps, C_MONTH_NM, 'None', mn_inst, 'nominal')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    clean_style(table)
    pane = make_pane(table, 'Bar')
    add_bar_mark_style(pane)

    finish_ws(ws, table, rows=fq(sr_inst), cols=fq(mn_inst))
    return ws


# ── Day-of-Week Pattern ───────────────────────────────────────────────────────

def build_dow_pattern():
    ws, table = ws_start('Day-of-Week Pattern', 'Day-of-Week Pattern')
    view, deps = make_view(table)

    sr     = C_SEL_RATE[1:-1]
    dn     = C_DOW_NM[1:-1]
    sr_inst = f'[avg:{sr}:qk]'
    dn_inst = f'[none:{dn}:nk]'

    dep_col(deps, C_SEL_RATE, 'Selected Rate', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_SEL_RATE, 'Avg', sr_inst, 'quantitative')
    dep_col(deps, C_DOW_NM, 'Day of Week', 'string', 'dimension', 'nominal')
    dep_ci(deps, C_DOW_NM, 'None', dn_inst, 'nominal')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    clean_style(table)
    pane = make_pane(table, 'Bar')
    add_bar_mark_style(pane)

    finish_ws(ws, table, rows=fq(sr_inst), cols=fq(dn_inst))
    return ws


# ── Volatility Line ───────────────────────────────────────────────────────────
# Uses Cumulative % Change (from first period), NOT period-over-period change.

def build_volatility_line():
    ws, table = ws_start('Volatility Line', 'Volatility — Cumulative Change %')
    view, deps = make_view(table)

    cc  = C_CUM_CHG[1:-1]
    sd  = C_SEL_DATE[1:-1]
    cc_inst = f'[usr:{cc}:qk]'
    sd_inst = f'[none:{sd}:nk]'

    dep_col(deps, C_SEL_DATE, 'Selected Date (Dynamic)', 'string', 'dimension', 'nominal')
    dep_ci(deps, C_SEL_DATE, 'None', sd_inst, 'nominal')
    dep_col(deps, C_CUM_CHG, 'Cumulative % Change', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_CUM_CHG, 'User', cc_inst, 'quantitative')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    clean_style(table)
    pane = make_pane(table, 'Line')
    sub(pane, 'mark-sizing', **{'mark-sizing-setting': 'marks-scaling-off'})
    add_line_mark_style(pane)

    finish_ws(ws, table, rows=fq(cc_inst), cols=fq(sd_inst))
    return ws


# ── Period Change Bars ────────────────────────────────────────────────────────
# Uses Period Change % (period-over-period).

def build_period_change_bars():
    ws, table = ws_start('Period Change Bars', 'Period Change Distribution')
    view, deps = make_view(table)

    pc  = C_PERIOD_C[1:-1]
    sd  = C_SEL_DATE[1:-1]
    pc_inst = f'[usr:{pc}:qk]'
    sd_inst = f'[none:{sd}:nk]'

    dep_col(deps, C_SEL_DATE, 'Selected Date (Dynamic)', 'string', 'dimension', 'nominal')
    dep_ci(deps, C_SEL_DATE, 'None', sd_inst, 'nominal')
    dep_col(deps, C_PERIOD_C, 'Period Change %', 'real', 'measure', 'quantitative')
    dep_ci(deps, C_PERIOD_C, 'User', pc_inst, 'quantitative')
    add_date_filter(view, deps)
    sub(view, 'aggregation', value='true')

    clean_style(table)
    pane = make_pane(table, 'Bar')
    add_bar_mark_style(pane)

    finish_ws(ws, table, rows=fq(pc_inst), cols=fq(sd_inst))
    return ws


# ── Multi-Currency Comparison ─────────────────────────────────────────────────
# Uses Measure Names / Measure Values to overlay all 5 currencies as colored lines.

def build_multi_currency():
    ws, table = ws_start('Multi-Currency Comparison', 'Multi-Currency Comparison')
    view, deps = make_view(table)

    sd = C_SEL_DATE[1:-1]
    sd_inst = f'[none:{sd}:nk]'

    dep_col(deps, C_SEL_DATE, 'Selected Date (Dynamic)', 'string', 'dimension', 'nominal')
    dep_ci(deps, C_SEL_DATE, 'None', sd_inst, 'nominal')

    # Add individual currency columns so they appear in Measure Values
    cur_map = {'USD': 'USD', 'GBP': 'GBP', 'JPY_100': 'JPY/100', 'EUR': 'EUR', 'CHF': 'CHF'}
    for cur, cap in cur_map.items():
        dep_col(deps, f'[{cur}]', cap, 'real', 'measure', 'quantitative')
        dep_ci(deps, f'[{cur}]', 'Avg', f'[avg:{cur}:qk]', 'quantitative')

    # Measure Names / Measure Values are native Tableau pivot fields — do NOT declare in deps

    add_date_filter(view, deps)

    # Measure Names filter — restrict to the 5 currencies
    # user:op='manual' goes on the UNION groupfilter, not on children
    f_mn = ET.SubElement(view, 'filter')
    f_mn.set('class', 'categorical')
    f_mn.set('column', fq('[:Measure Names]'))
    gf_union = ET.SubElement(f_mn, 'groupfilter')
    gf_union.set('function', 'union')
    gf_union.set('user:op', 'manual')
    for cur in CURRENCIES:
        gf = ET.SubElement(gf_union, 'groupfilter')
        gf.set('function', 'member')
        gf.set('level', '[:Measure Names]')
        gf.set('member', f'"[{DS_NAME}].[avg:{cur}:qk]"')

    sub(view, 'aggregation', value='true')

    clean_style(table)
    pane = make_pane(table, 'Line')
    add_encoding(pane, 'color', fq('[:Measure Names]'))

    finish_ws(ws, table,
              rows=fq('[Multiple Values]'),
              cols=fq(sd_inst))
    return ws


# ── Dashboard ─────────────────────────────────────────────────────────────────

def build_dashboard(dash_uuid):
    """
    Layout (top→bottom):
      Header: title + subtitle text zone
      Controls Row: 4 parameter controls
      KPI Row: 4 KPI cards (distribute-evenly)
      Main Trend Line: full-width dual-axis line+area
      Seasonality Row: Monthly Seasonality | Day-of-Week Pattern (50/50)
      Volatility Row: Volatility Line | Period Change Bars (50/50)
      Multi-Currency Comparison: full-width
      Footer: Created by Niv Levi
    """
    db = ET.Element('dashboard', name=DASH_NAME)
    sub(db, 'style')
    sz = sub(db, 'size')
    sz.set('maxheight', '1700')
    sz.set('maxwidth', '1400')
    sz.set('minheight', '1700')
    sz.set('minwidth', '1400')
    sz.set('sizing-mode', 'fixed')

    zones = ET.SubElement(db, 'zones')

    # ── Zone ID counter ──────────────────────────────────────────────────────
    z_id = [1]
    def nid():
        z_id[0] += 1
        return str(z_id[0])

    # ── Root layout-basic ────────────────────────────────────────────────────
    root = ET.SubElement(zones, 'zone')
    root.set('h', '100000'); root.set('id', '1')
    root.set('type-v2', 'layout-basic')
    root.set('w', '100000'); root.set('x', '0'); root.set('y', '0')

    # ── Main vertical flow ───────────────────────────────────────────────────
    main_flow = ET.SubElement(root, 'zone')
    main_flow.set('h', '100000'); main_flow.set('id', nid())
    main_flow.set('param', 'vert'); main_flow.set('type-v2', 'layout-flow')
    main_flow.set('w', '100000'); main_flow.set('x', '0'); main_flow.set('y', '0')
    main_flow.set('friendly-name', 'Main Section')

    # Dashboard title + subtitle header
    title_z = ET.SubElement(main_flow, 'zone')
    title_z.set('forceUpdate', 'true')
    title_z.set('h', '4589'); title_z.set('id', nid())
    title_z.set('type-v2', 'text')
    title_z.set('w', '100000'); title_z.set('x', '0'); title_z.set('y', '0')
    ft_title = ET.SubElement(title_z, 'formatted-text')
    rt = ET.SubElement(ft_title, 'run')
    rt.set('fontalignment', '1')
    rt.set('fontcolor', '#006ce0')
    rt.set('fontname', 'Tableau Bold')
    rt.set('fontsize', '24')
    rt.text = 'NIS Forex Exchange Rate Dashboard'
    # Newline separator
    sep = ET.SubElement(ft_title, 'run')
    sep.set('fontalignment', '1')
    sep.text = '\n'
    # Subtitle
    sub_run = ET.SubElement(ft_title, 'run')
    sub_run.set('fontalignment', '1')
    sub_run.set('fontcolor', '#555555')
    sub_run.set('fontname', 'Tableau Bold')
    sub_run.set('fontsize', '14')
    sub_run.text = 'Generated by Tableau AI Skill'
    tzs = ET.SubElement(title_z, 'zone-style')
    fmt(tzs, 'border-color', '#000000')
    fmt(tzs, 'border-style', 'none')
    fmt(tzs, 'border-width', '0')
    fmt(tzs, 'margin', '4')

    # Controls Row — 4 parameter controls
    ctrl_row = ET.SubElement(main_flow, 'zone')
    ctrl_row.set('fixed-size', '74'); ctrl_row.set('h', '4353')
    ctrl_row.set('id', nid()); ctrl_row.set('is-fixed', 'true')
    ctrl_row.set('param', 'horz'); ctrl_row.set('type-v2', 'layout-flow')
    ctrl_row.set('w', '100000'); ctrl_row.set('x', '0'); ctrl_row.set('y', '0')
    ctrl_row.set('friendly-name', 'Controls Row')

    for pname in [P_CURRENCY, P_GRANUL, P_START, P_END]:
        pz = ET.SubElement(ctrl_row, 'zone')
        pz.set('fixed-size', '200'); pz.set('h', '4353')
        pz.set('id', nid()); pz.set('is-fixed', 'true')
        pz.set('mode', 'compact' if 'Parameter 3' not in pname and 'Parameter 4' not in pname else 'datetime')
        pz.set('param', f'[Parameters].{pname}')
        pz.set('type-v2', 'paramctrl')
        pz.set('w', '14286'); pz.set('x', '0'); pz.set('y', '0')
        pzs = ET.SubElement(pz, 'zone-style')
        fmt(pzs, 'border-color', '#000000')
        fmt(pzs, 'border-style', 'none')
        fmt(pzs, 'border-width', '0')
        fmt(pzs, 'background-color', '#ffffff')

    # KPI Row — 4 cards (distribute-evenly)
    kpi_row = ET.SubElement(main_flow, 'zone')
    kpi_row.set('fixed-size', '160'); kpi_row.set('h', '9412')
    kpi_row.set('id', nid()); kpi_row.set('is-fixed', 'true')
    kpi_row.set('layout-strategy-id', 'distribute-evenly')
    kpi_row.set('param', 'horz'); kpi_row.set('type-v2', 'layout-flow')
    kpi_row.set('w', '100000'); kpi_row.set('x', '0'); kpi_row.set('y', '0')
    kpi_row.set('friendly-name', 'KPI Row')

    for kpi_name in ['KPI Avg Rate', 'KPI Period High', 'KPI Period Low', 'KPI Data Points']:
        kpi_wrap = ET.SubElement(kpi_row, 'zone')
        kpi_wrap.set('h', '9411'); kpi_wrap.set('id', nid())
        kpi_wrap.set('param', 'vert'); kpi_wrap.set('type-v2', 'layout-flow')
        kpi_wrap.set('w', '25000'); kpi_wrap.set('x', '0'); kpi_wrap.set('y', '0')
        kpi_wrap.set('friendly-name', f'{kpi_name} Card')

        kz = ET.SubElement(kpi_wrap, 'zone')
        kz.set('h', '9411'); kz.set('id', nid())
        kz.set('name', kpi_name)
        kz.set('w', '25000'); kz.set('x', '0'); kz.set('y', '0')
        kzs = ET.SubElement(kz, 'zone-style')
        fmt(kzs, 'border-color', '#555555')
        fmt(kzs, 'border-style', 'solid')
        fmt(kzs, 'border-width', '1')
        ET.SubElement(kzs, '_.fcp.DashboardRoundedCorners.true...format').set('attr', 'corner-radius'), kzs[-1].set('value', '8')
        fmt(kzs, 'margin', '6')
        fmt(kzs, 'padding', '8')
        fmt(kzs, 'background-color', '#f5f5f5')

    # Main Trend Line — full width
    trend_row = ET.SubElement(main_flow, 'zone')
    trend_row.set('fixed-size', '288'); trend_row.set('h', '17647')
    trend_row.set('id', nid()); trend_row.set('is-fixed', 'true')
    trend_row.set('name', 'Main Trend Line')
    trend_row.set('w', '100000'); trend_row.set('x', '0'); trend_row.set('y', '0')
    trs = ET.SubElement(trend_row, 'zone-style')
    fmt(trs, 'border-color', '#555555')
    fmt(trs, 'border-style', 'solid')
    fmt(trs, 'border-width', '1')
    ET.SubElement(trs, '_.fcp.DashboardRoundedCorners.true...format').set('attr', 'corner-radius'), trs[-1].set('value', '8')
    fmt(trs, 'margin', '6')
    fmt(trs, 'background-color', '#f5f5f5')

    # Seasonality Row — Monthly | DoW (50/50)
    row_seas = ET.SubElement(main_flow, 'zone')
    row_seas.set('h', '20087'); row_seas.set('id', nid())
    row_seas.set('layout-strategy-id', 'distribute-evenly')
    row_seas.set('param', 'horz'); row_seas.set('type-v2', 'layout-flow')
    row_seas.set('w', '100000'); row_seas.set('x', '0'); row_seas.set('y', '0')
    row_seas.set('friendly-name', 'Seasonality Row')

    for sheet in ['Monthly Seasonality', 'Day-of-Week Pattern']:
        z = ET.SubElement(row_seas, 'zone')
        z.set('h', '20118'); z.set('id', nid())
        z.set('name', sheet)
        z.set('w', '50000'); z.set('x', '0'); z.set('y', '0')
        zs = ET.SubElement(z, 'zone-style')
        fmt(zs, 'border-color', '#555555')
        fmt(zs, 'border-style', 'solid')
        fmt(zs, 'border-width', '1')
        ET.SubElement(zs, '_.fcp.DashboardRoundedCorners.true...format').set('attr', 'corner-radius'), zs[-1].set('value', '8')
        fmt(zs, 'margin', '6')
        fmt(zs, 'background-color', '#f5f5f5')

    # Volatility Row — Volatility Line | Period Change Bars (50/50)
    row_vol = ET.SubElement(main_flow, 'zone')
    row_vol.set('h', '20146'); row_vol.set('id', nid())
    row_vol.set('layout-strategy-id', 'distribute-evenly')
    row_vol.set('param', 'horz'); row_vol.set('type-v2', 'layout-flow')
    row_vol.set('w', '100000'); row_vol.set('x', '0'); row_vol.set('y', '0')
    row_vol.set('friendly-name', 'Volatility Row')

    for sheet in ['Volatility Line', 'Period Change Bars']:
        z = ET.SubElement(row_vol, 'zone')
        z.set('h', '20118'); z.set('id', nid())
        z.set('name', sheet)
        z.set('w', '50000'); z.set('x', '0'); z.set('y', '0')
        zs = ET.SubElement(z, 'zone-style')
        fmt(zs, 'border-color', '#555555')
        fmt(zs, 'border-style', 'solid')
        fmt(zs, 'border-width', '1')
        ET.SubElement(zs, '_.fcp.DashboardRoundedCorners.true...format').set('attr', 'corner-radius'), zs[-1].set('value', '8')
        fmt(zs, 'margin', '6')
        fmt(zs, 'background-color', '#f5f5f5')

    # Multi-Currency Comparison — full width
    mcc = ET.SubElement(main_flow, 'zone')
    mcc.set('fixed-size', '342'); mcc.set('h', '20824')
    mcc.set('id', nid()); mcc.set('is-fixed', 'true')
    mcc.set('name', 'Multi-Currency Comparison')
    mcc.set('w', '100000'); mcc.set('x', '0'); mcc.set('y', '0')
    mccs = ET.SubElement(mcc, 'zone-style')
    fmt(mccs, 'border-color', '#555555')
    fmt(mccs, 'border-style', 'solid')
    fmt(mccs, 'border-width', '1')
    ET.SubElement(mccs, '_.fcp.DashboardRoundedCorners.true...format').set('attr', 'corner-radius'), mccs[-1].set('value', '8')
    fmt(mccs, 'margin', '6')
    fmt(mccs, 'background-color', '#f5f5f5')

    # Footer
    footer = ET.SubElement(main_flow, 'zone')
    footer.set('fixed-size', '30'); footer.set('h', '1765')
    footer.set('id', nid()); footer.set('is-fixed', 'true')
    footer.set('type-v2', 'text')
    footer.set('w', '100000'); footer.set('x', '0'); footer.set('y', '0')
    ft = ET.SubElement(footer, 'formatted-text')
    run = ET.SubElement(ft, 'run')
    run.set('fontcolor', '#888888')
    run.set('fontname', 'Tableau Book')
    run.set('fontsize', '9')
    run.text = 'Created by Niv Levi'

    # zone-style MUST be last child of root zone
    zs_root = ET.SubElement(root, 'zone-style')
    fmt(zs_root, 'border-color', '#000000')
    fmt(zs_root, 'border-style', 'none')
    fmt(zs_root, 'border-width', '0')
    fmt(zs_root, 'background-color', '#ffffff')

    sub(db, 'simple-id', uuid=dash_uuid)
    return db


# ── Windows section ───────────────────────────────────────────────────────────

def build_windows(dash_uuid):
    windows = ET.Element('windows')

    # Dashboard window
    dw = ET.SubElement(windows, 'window')
    dw.set('class', 'dashboard')
    dw.set('maximized', 'true')
    dw.set('name', DASH_NAME)
    vps = ET.SubElement(dw, 'viewpoints')
    for sname in SHEET_NAMES:
        vp = ET.SubElement(vps, 'viewpoint')
        vp.set('name', sname)
        ET.SubElement(vp, 'zoom').set('type', 'entire-view')
    sub(dw, 'active', id='-1')
    sub(dw, 'simple-id', uuid=dash_uuid)

    # Worksheet windows
    for sname in SHEET_NAMES:
        w = ET.SubElement(windows, 'window')
        w.set('class', 'worksheet')
        w.set('hidden', 'true')
        w.set('name', sname)
        cards = ET.SubElement(w, 'cards')
        left = ET.SubElement(cards, 'edge'); left.set('name', 'left')
        strip = ET.SubElement(left, 'strip'); strip.set('size', '160')
        for ct in ['pages', 'filters', 'marks']:
            ET.SubElement(strip, 'card').set('type', ct)
        top = ET.SubElement(cards, 'edge'); top.set('name', 'top')
        for ct, sz in [('columns', '2147483647'), ('rows', '2147483647'), ('title', '2147483647')]:
            s = ET.SubElement(top, 'strip'); s.set('size', sz)
            ET.SubElement(s, 'card').set('type', ct)
        vp = ET.SubElement(w, 'viewpoint')
        ET.SubElement(vp, 'zoom').set('type', 'entire-view')
        sub(w, 'simple-id', uuid=new_uuid())

    return windows


# ── Workbook assembly ─────────────────────────────────────────────────────────

def build_workbook():
    wb = ET.Element('workbook')
    wb.set('source-build', '2026.1.0 (20261.26.0410.1059)')
    wb.set('version', '18.1')
    wb.set('xmlns:user', 'http://www.tableausoftware.com/xml/user')

    # Manifest
    manifest = ET.SubElement(wb, 'document-format-change-manifest')
    for entry in [
        'AnimationOnByDefault',
        '_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners',
        'MarkAnimation',
        'ObjectModelEncapsulateLegacy',
        'ObjectModelExtractV2',
        'ObjectModelTableType',
        'SchemaViewerObjectModel',
        'SetMembershipControl',
        'SheetIdentifierTracking',
        '_.fcp.VConnDownstreamExtractsWithWarnings.true...VConnDownstreamExtractsWithWarnings',
        'WindowsPersistSimpleIdentifiers',
        'WorksheetBackgroundTransparency',
        'ZoneFriendlyName',
    ]:
        ET.SubElement(manifest, entry)

    # Preferences
    prefs = ET.SubElement(wb, 'preferences')
    sub(prefs, 'preference', name='ui.encoding.shelf.height', value='250')
    sub(prefs, 'preference', name='ui.shelf.height', value='250')

    # Datasources
    datasources = ET.SubElement(wb, 'datasources')
    datasources.append(build_params_ds())
    datasources.append(build_data_ds())

    # Worksheets
    worksheets = ET.SubElement(wb, 'worksheets')
    for ws_fn in [
        build_kpi_avg_rate, build_kpi_period_high,
        build_kpi_period_low, build_kpi_data_points,
        build_main_trend, build_monthly_seasonality,
        build_dow_pattern, build_volatility_line,
        build_period_change_bars, build_multi_currency,
    ]:
        worksheets.append(ws_fn())

    # Dashboard
    dash_uuid = new_uuid()
    dashboards = ET.SubElement(wb, 'dashboards')
    dashboards.append(build_dashboard(dash_uuid))

    # Windows
    wb.append(build_windows(dash_uuid))

    return wb


# ── Post-processing: fix element names that ElementTree escapes ───────────────

def postprocess(xml_str: str) -> str:
    replacements = [
        ('&lt;_.fcp.DashboardRoundedCorners.true...format',
         '<_.fcp.DashboardRoundedCorners.true...format'),
        ('&lt;/_.fcp.DashboardRoundedCorners.true...format',
         '</_.fcp.DashboardRoundedCorners.true...format'),
        ('&lt;_.fcp.ObjectModelEncapsulateLegacy.true...ObjectModelEncapsulateLegacy',
         '<_.fcp.ObjectModelEncapsulateLegacy.true...ObjectModelEncapsulateLegacy'),
        ('&lt;/_.fcp.ObjectModelEncapsulateLegacy.true...ObjectModelEncapsulateLegacy',
         '</_.fcp.ObjectModelEncapsulateLegacy.true...ObjectModelEncapsulateLegacy'),
        ('&lt;_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners',
         '<_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners'),
        ('&lt;/_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners',
         '</_.fcp.DashboardRoundedCorners.true...DashboardRoundedCorners'),
        ('&lt;_.fcp.VConnDownstreamExtractsWithWarnings.true...VConnDownstreamExtractsWithWarnings',
         '<_.fcp.VConnDownstreamExtractsWithWarnings.true...VConnDownstreamExtractsWithWarnings'),
        ('&lt;/_.fcp.VConnDownstreamExtractsWithWarnings.true...VConnDownstreamExtractsWithWarnings',
         '</_.fcp.VConnDownstreamExtractsWithWarnings.true...VConnDownstreamExtractsWithWarnings'),
    ]
    for old, new in replacements:
        xml_str = xml_str.replace(old, new)
    return xml_str


# ── Tier-2 structural validation ──────────────────────────────────────────────

def validate(xml_str: str, ws_names: list, dash_name: str) -> bool:
    import xml.etree.ElementTree as ET2
    try:
        root = ET2.fromstring(xml_str.encode('utf-8'))
    except ET2.ParseError as e:
        print(f'[FAIL] XML parse error: {e}')
        return False

    errors = []
    defined_ws = {ws.get('name') for ws in root.findall('.//worksheets/worksheet')}

    for ws_name in ws_names:
        if ws_name not in defined_ws:
            errors.append(f'Worksheet missing: {ws_name}')

    for zone in root.findall('.//zones//zone[@name]'):
        zname = zone.get('name')
        if zname and zname not in defined_ws and zname != dash_name:
            errors.append(f'Zone name not in worksheets: {zname!r}')

    for ws in root.findall('.//worksheets/worksheet'):
        if ws.find('simple-id') is None:
            errors.append(f'Missing simple-id on worksheet: {ws.get("name")}')
    for db in root.findall('.//dashboards/dashboard'):
        if db.find('simple-id') is None:
            errors.append(f'Missing simple-id on dashboard: {db.get("name")}')

    zone_ids = [z.get('id') for z in root.findall('.//zone[@id]')]
    from collections import Counter
    for zid, cnt in Counter(zone_ids).items():
        if cnt > 1:
            errors.append(f'Duplicate zone id: {zid}')

    if errors:
        print('Validation FAILED:')
        for e in errors:
            print(f'  - {e}')
        return False
    print('Validation PASSED')
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    output_path = Path('nis_forex_dashboard.twb')

    print('Building workbook XML...')
    wb = build_workbook()

    raw = ET.tostring(wb, encoding='unicode', xml_declaration=False)
    xml_str = "<?xml version='1.0' encoding='utf-8' ?>\n" + raw
    xml_str = postprocess(xml_str)

    # Pretty-print
    try:
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_str.encode('utf-8'))
        xml_str = "<?xml version='1.0' encoding='utf-8' ?>\n" + dom.toprettyxml(indent='  ')[23:]
        xml_str = postprocess(xml_str)  # minidom may re-escape; run again
    except Exception:
        pass  # fall back to compact output

    if not validate(xml_str, SHEET_NAMES, DASH_NAME):
        print('Fix errors before opening in Tableau Desktop.')

    output_path.write_text(xml_str, encoding='utf-8')
    print(f'Saved: {output_path.resolve()}')
    print(f'Sheets: {len(SHEET_NAMES)}, Dashboard: {DASH_NAME}')
    print(f'CSV dir embedded:  {CSV_DIR}')
    print(f'CSV file embedded: {CSV_FILE}')
    print('Open in Tableau Desktop 2026.1+ and re-point data source if needed.')


if __name__ == '__main__':
    main()
