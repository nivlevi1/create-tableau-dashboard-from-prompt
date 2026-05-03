#!/usr/bin/env python3
"""
Tableau TWB Generator - Generate Tableau workbook XML files programmatically.

Usage:
    from generate_twb import TableauWorkbook
    
    wb = TableauWorkbook()
    wb.add_excel_datasource('MyData', '/path/to/file.xlsx', 'Sheet1')
    wb.add_worksheet('Sales Chart', 'MyData', 
                     rows='[sum:Sales:qk]', 
                     cols='[none:Category:nk]',
                     mark_type='Bar')
    wb.save('output.twb')
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid
import zipfile
from pathlib import Path
from typing import Optional, List, Dict


class TableauWorkbook:
    """Generate Tableau TWB workbook files."""
    
    def __init__(self, version: str = '18.1', platform: str = 'win'):
        self.version = version
        self.platform = platform
        self.datasources: Dict[str, ET.Element] = {}
        self.worksheets: List[ET.Element] = []
        self.dashboards: List[ET.Element] = []
        self.parameters: List[ET.Element] = []
    
    def _generate_id(self) -> str:
        """Generate a unique identifier."""
        return str(uuid.uuid4()).replace('-', '')[:20]
    
    def add_parameter(self, name: str, datatype: str = 'integer', 
                      default_value: str = '1',
                      min_value: Optional[str] = None,
                      max_value: Optional[str] = None,
                      granularity: Optional[str] = None) -> str:
        """Add a parameter to the workbook."""
        param_num = len(self.parameters) + 1
        internal_name = f'[Parameter {param_num}]'
        
        col = ET.Element('column')
        col.set('caption', name)
        col.set('datatype', datatype)
        col.set('name', internal_name)
        col.set('param-domain-type', 'range')
        col.set('role', 'measure')
        col.set('type', 'quantitative')
        col.set('value', default_value)
        
        calc = ET.SubElement(col, 'calculation')
        calc.set('class', 'tableau')
        calc.set('formula', default_value)
        
        if min_value is not None or max_value is not None:
            range_elem = ET.SubElement(col, 'range')
            if granularity:
                range_elem.set('granularity', granularity)
            if min_value:
                range_elem.set('min', min_value)
            if max_value:
                range_elem.set('max', max_value)
        
        self.parameters.append(col)
        return internal_name
    
    def add_excel_datasource(self, name: str, filepath: str, 
                              sheet_name: str,
                              columns: Optional[List[Dict]] = None) -> str:
        """
        Add an Excel data source.
        
        Args:
            name: Display name for the datasource
            filepath: Path to Excel file
            sheet_name: Name of the sheet to use
            columns: List of column definitions: [{'name': 'Col1', 'datatype': 'string'}, ...]
        
        Returns:
            Internal datasource name
        """
        ds_id = f'federated.{self._generate_id()}'
        
        ds = ET.Element('datasource')
        ds.set('caption', name)
        ds.set('inline', 'true')
        ds.set('name', ds_id)
        ds.set('version', self.version)
        
        # Connection
        conn_id = f'excel-direct.{self._generate_id()}'
        named_conn = ET.SubElement(ds, 'named-connection')
        named_conn.set('caption', name)
        named_conn.set('name', conn_id)
        
        conn = ET.SubElement(named_conn, 'connection')
        conn.set('class', 'excel-direct')
        conn.set('cleaning', 'no')
        conn.set('compat', 'no')
        conn.set('filename', filepath)
        conn.set('validate', 'no')
        
        # Relation
        relation = ET.SubElement(ds, 'relation')
        relation.set('connection', conn_id)
        relation.set('name', sheet_name)
        relation.set('table', f'[{sheet_name}$]')
        relation.set('type', 'table')
        
        if columns:
            cols_elem = ET.SubElement(relation, 'columns')
            cols_elem.set('header', 'yes')
            cols_elem.set('outcome', '6')
            for i, col in enumerate(columns):
                col_elem = ET.SubElement(cols_elem, 'column')
                col_elem.set('datatype', col.get('datatype', 'string'))
                col_elem.set('name', col['name'])
                col_elem.set('ordinal', str(i))
        
        # Aliases
        aliases = ET.SubElement(ds, 'aliases')
        aliases.set('enabled', 'yes')
        
        self.datasources[name] = ds
        return ds_id
    
    def add_database_datasource(self, name: str, connection_class: str,
                                 server: str, database: str,
                                 schema: Optional[str] = None,
                                 port: Optional[str] = None,
                                 username: Optional[str] = None,
                                 tables: Optional[List[Dict]] = None) -> str:
        """
        Add a database data source.
        
        Args:
            name: Display name
            connection_class: Connection type (sqlserver, postgres, databricks, etc.)
            server: Server hostname
            database: Database name
            schema: Schema name (optional)
            port: Port number (optional)
            username: Username (optional)
            tables: List of tables: [{'name': 'Orders', 'table': '[dbo].[Orders]'}, ...]
        
        Returns:
            Internal datasource name
        """
        ds_id = f'federated.{self._generate_id()}'
        
        ds = ET.Element('datasource')
        ds.set('caption', name)
        ds.set('inline', 'true')
        ds.set('name', ds_id)
        ds.set('version', self.version)
        
        # Connection
        conn = ET.SubElement(ds, 'connection')
        conn.set('class', connection_class)
        conn.set('dbname', database)
        conn.set('server', server)
        if port:
            conn.set('port', port)
        if schema:
            conn.set('schema', schema)
        if username:
            conn.set('username', username)
        
        # Tables
        if tables:
            for tbl in tables:
                relation = ET.SubElement(conn, 'relation')
                relation.set('name', tbl['name'])
                relation.set('table', tbl['table'])
                relation.set('type', 'table')
        
        # Aliases
        aliases = ET.SubElement(ds, 'aliases')
        aliases.set('enabled', 'yes')
        
        self.datasources[name] = ds
        return ds_id
    
    def add_calculated_field(self, datasource_name: str, 
                              field_name: str, 
                              formula: str,
                              datatype: str = 'real',
                              role: str = 'measure',
                              default_format: Optional[str] = None) -> str:
        """Add a calculated field to a datasource."""
        if datasource_name not in self.datasources:
            raise ValueError(f"Datasource '{datasource_name}' not found")
        
        ds = self.datasources[datasource_name]
        calc_id = f'Calculation_{self._generate_id()}'
        
        col = ET.SubElement(ds, 'column')
        col.set('caption', field_name)
        col.set('datatype', datatype)
        col.set('name', f'[{calc_id}]')
        col.set('role', role)
        col.set('type', 'quantitative' if role == 'measure' else 'nominal')
        if default_format:
            col.set('default-format', default_format)
        
        calc = ET.SubElement(col, 'calculation')
        calc.set('class', 'tableau')
        calc.set('formula', formula)
        
        return f'[{calc_id}]'
    
    def add_worksheet(self, name: str, datasource_name: str,
                      rows: str, cols: str,
                      mark_type: str = 'Automatic',
                      filters: Optional[List[Dict]] = None,
                      color: Optional[str] = None,
                      size: Optional[str] = None,
                      label: Optional[str] = None) -> None:
        """
        Add a worksheet.
        
        Args:
            name: Worksheet name
            datasource_name: Name of datasource to use
            rows: Fields for rows shelf (e.g., '[sum:Sales:qk]')
            cols: Fields for columns shelf (e.g., '[none:Category:nk]')
            mark_type: Mark type (Bar, Line, Circle, etc.)
            filters: List of filters: [{'class': 'categorical', 'column': '[Field]'}, ...]
            color: Field for color encoding
            size: Field for size encoding
            label: Field for label/text encoding
        """
        if datasource_name not in self.datasources:
            raise ValueError(f"Datasource '{datasource_name}' not found")
        
        ds = self.datasources[datasource_name]
        ds_id = ds.get('name')
        
        ws = ET.Element('worksheet')
        ws.set('name', name)
        
        table = ET.SubElement(ws, 'table')
        view = ET.SubElement(table, 'view')
        
        # Datasource reference
        datasources = ET.SubElement(view, 'datasources')
        ds_ref = ET.SubElement(datasources, 'datasource')
        ds_ref.set('name', ds_id)
        
        # Add Parameters datasource if parameters exist
        if self.parameters:
            params_ref = ET.SubElement(datasources, 'datasource')
            params_ref.set('name', 'Parameters')
        
        # Filters
        if filters:
            for f in filters:
                filt = ET.SubElement(view, 'filter')
                filt.set('class', f.get('class', 'categorical'))
                filt.set('column', f'[{ds_id}].{f["column"]}')
        
        # Rows and Cols
        rows_elem = ET.SubElement(view, 'rows')
        rows_elem.text = f'[{ds_id}].{rows}' if not rows.startswith('[') else f'[{ds_id}].{rows}'
        
        cols_elem = ET.SubElement(view, 'cols')
        cols_elem.text = f'[{ds_id}].{cols}' if not cols.startswith('[') else f'[{ds_id}].{cols}'
        
        # Style
        style = ET.SubElement(table, 'style')
        style_rule = ET.SubElement(style, 'style-rule')
        style_rule.set('element', 'mark')
        mark = ET.SubElement(style_rule, 'mark')
        mark.set('class', mark_type)
        
        # Panes with encodings
        panes = ET.SubElement(table, 'panes')
        pane = ET.SubElement(panes, 'pane')
        mark_pane = ET.SubElement(pane, 'mark')
        mark_pane.set('class', mark_type)
        
        if color or size or label:
            encodings = ET.SubElement(pane, 'encodings')
            if color:
                enc = ET.SubElement(encodings, 'color')
                enc.set('column', f'[{ds_id}].{color}')
            if size:
                enc = ET.SubElement(encodings, 'size')
                enc.set('column', f'[{ds_id}].{size}')
            if label:
                enc = ET.SubElement(encodings, 'text')
                enc.set('column', f'[{ds_id}].{label}')
        
        self.worksheets.append(ws)
    
    def add_dashboard(self, name: str, 
                      worksheet_layout: List[Dict],
                      width: int = 1300, height: int = 900) -> None:
        """
        Add a dashboard.
        
        Args:
            name: Dashboard name
            worksheet_layout: Layout specification:
                [{'name': 'Sheet1', 'x': 0, 'y': 0, 'w': 50000, 'h': 100000}, ...]
            width: Dashboard width
            height: Dashboard height
        """
        db = ET.Element('dashboard')
        db.set('name', name)
        
        # Size
        size = ET.SubElement(db, 'size')
        size.set('maxwidth', str(width))
        size.set('maxheight', str(height))
        
        # Zones
        zones = ET.SubElement(db, 'zones')
        container = ET.SubElement(zones, 'zone')
        container.set('h', '100000')
        container.set('id', '1')
        container.set('type', 'layout-basic')
        container.set('w', '100000')
        container.set('x', '0')
        container.set('y', '0')
        
        for i, layout in enumerate(worksheet_layout):
            zone = ET.SubElement(container, 'zone')
            zone.set('h', str(layout.get('h', 100000)))
            zone.set('id', str(i + 2))
            zone.set('name', layout['name'])
            zone.set('type', 'worksheet')
            zone.set('w', str(layout.get('w', 100000)))
            zone.set('x', str(layout.get('x', 0)))
            zone.set('y', str(layout.get('y', 0)))
        
        self.dashboards.append(db)
    
    def to_xml(self) -> str:
        """Generate the complete TWB XML."""
        root = ET.Element('workbook')
        root.set('source-platform', self.platform)
        root.set('version', self.version)
        root.set('xmlns:user', 'http://www.tableausoftware.com/xml/user')
        
        # Preferences
        prefs = ET.SubElement(root, 'preferences')
        pref = ET.SubElement(prefs, 'preference')
        pref.set('name', 'ui.encoding.shelf.height')
        pref.set('value', '250')
        
        # Datasources
        datasources = ET.SubElement(root, 'datasources')
        
        # Add Parameters datasource if we have parameters
        if self.parameters:
            params_ds = ET.SubElement(datasources, 'datasource')
            params_ds.set('hasconnection', 'false')
            params_ds.set('inline', 'true')
            params_ds.set('name', 'Parameters')
            params_ds.set('version', self.version)
            aliases = ET.SubElement(params_ds, 'aliases')
            aliases.set('enabled', 'yes')
            for param in self.parameters:
                params_ds.append(param)
        
        # Add data datasources
        for ds in self.datasources.values():
            datasources.append(ds)
        
        # Worksheets
        worksheets = ET.SubElement(root, 'worksheets')
        for ws in self.worksheets:
            worksheets.append(ws)
        
        # Dashboards
        if self.dashboards:
            dashboards = ET.SubElement(root, 'dashboards')
            for db in self.dashboards:
                dashboards.append(db)
        
        # Pretty print
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return '<?xml version="1.0" encoding="utf-8"?>\n' + dom.toprettyxml(indent='  ')[23:]  # Skip XML declaration from minidom
    
    def save(self, filepath: str) -> None:
        """Save workbook to file."""
        xml_content = self.to_xml()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    
    def save_twbx(self, filepath: str, data_files: Optional[Dict[str, str]] = None) -> None:
        """
        Save as packaged workbook (TWBX).
        
        Args:
            filepath: Output TWBX path
            data_files: Dict mapping internal path to local file path
                       e.g., {'Data/Extract/file.hyper': '/local/path/file.hyper'}
        """
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as z:
            # Write TWB
            twb_name = Path(filepath).stem + '.twb'
            z.writestr(twb_name, self.to_xml())
            
            # Write data files
            if data_files:
                for internal_path, local_path in data_files.items():
                    z.write(local_path, internal_path)


# Example usage
if __name__ == '__main__':
    wb = TableauWorkbook()
    
    # Add a parameter
    wb.add_parameter('Top N', datatype='integer', default_value='10',
                     min_value='5', max_value='50', granularity='5')
    
    # Add Excel datasource
    wb.add_excel_datasource(
        'Sales Data', 
        '/path/to/sales.xlsx',
        'Orders',
        columns=[
            {'name': 'Category', 'datatype': 'string'},
            {'name': 'Sales', 'datatype': 'real'},
            {'name': 'Profit', 'datatype': 'real'},
            {'name': 'Order Date', 'datatype': 'date'}
        ]
    )
    
    # Add calculated field
    wb.add_calculated_field(
        'Sales Data',
        'Profit Ratio',
        'SUM([Profit])/SUM([Sales])',
        default_format='p0%'
    )
    
    # Add worksheet
    wb.add_worksheet(
        'Sales by Category',
        'Sales Data',
        rows='[sum:Sales:qk]',
        cols='[none:Category:nk]',
        mark_type='Bar',
        color='[none:Category:nk]'
    )
    
    # Add dashboard
    wb.add_dashboard(
        'Overview',
        [{'name': 'Sales by Category', 'x': 0, 'y': 0, 'w': 100000, 'h': 100000}]
    )
    
    # Save
    wb.save('example_workbook.twb')
    print("Workbook saved to example_workbook.twb")
