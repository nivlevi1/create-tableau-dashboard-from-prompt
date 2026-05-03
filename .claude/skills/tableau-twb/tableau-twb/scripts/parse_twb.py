#!/usr/bin/env python3
"""
Tableau TWB Parser - Extract information from Tableau workbook files.

Usage:
    python parse_twb.py workbook.twb
    python parse_twb.py workbook.twbx
"""

import sys
import xml.etree.ElementTree as ET
import zipfile
import json
from pathlib import Path


def extract_twb_from_twbx(twbx_path: str) -> str:
    """Extract TWB content from TWBX (zipped) file."""
    with zipfile.ZipFile(twbx_path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.twb'):
                return z.read(name).decode('utf-8')
    raise ValueError(f"No .twb file found in {twbx_path}")


def parse_workbook(file_path: str) -> dict:
    """Parse a Tableau workbook file and extract metadata."""
    path = Path(file_path)
    
    if path.suffix.lower() == '.twbx':
        xml_content = extract_twb_from_twbx(file_path)
        root = ET.fromstring(xml_content)
    else:
        tree = ET.parse(file_path)
        root = tree.getroot()
    
    workbook = {
        'version': root.get('version'),
        'source_build': root.get('source-build'),
        'source_platform': root.get('source-platform'),
        'datasources': [],
        'worksheets': [],
        'dashboards': [],
        'parameters': [],
        'calculated_fields': []
    }
    
    # Parse datasources
    for ds in root.findall('.//datasource'):
        ds_name = ds.get('name')
        ds_caption = ds.get('caption', ds_name)
        
        if ds_name == 'Parameters':
            # Extract parameters
            for col in ds.findall('column'):
                param = {
                    'name': col.get('name'),
                    'caption': col.get('caption'),
                    'datatype': col.get('datatype'),
                    'value': col.get('value')
                }
                calc = col.find('calculation')
                if calc is not None:
                    param['default_formula'] = calc.get('formula')
                range_elem = col.find('range')
                if range_elem is not None:
                    param['range'] = {
                        'min': range_elem.get('min'),
                        'max': range_elem.get('max'),
                        'granularity': range_elem.get('granularity')
                    }
                workbook['parameters'].append(param)
        else:
            # Regular datasource
            datasource = {
                'name': ds_name,
                'caption': ds_caption,
                'connection': None,
                'tables': [],
                'columns': []
            }
            
            # Connection info
            conn = ds.find('.//connection')
            if conn is not None:
                datasource['connection'] = {
                    'class': conn.get('class'),
                    'server': conn.get('server'),
                    'dbname': conn.get('dbname'),
                    'filename': conn.get('filename'),
                    'schema': conn.get('schema')
                }
            
            # Tables/relations
            for rel in ds.findall('.//relation[@type="table"]'):
                datasource['tables'].append({
                    'name': rel.get('name'),
                    'table': rel.get('table')
                })
            
            # Custom SQL
            for rel in ds.findall('.//relation[@type="text"]'):
                datasource['tables'].append({
                    'name': rel.get('name'),
                    'type': 'custom_sql',
                    'query': rel.text
                })
            
            # Columns
            for col in ds.findall('column'):
                column = {
                    'name': col.get('name'),
                    'caption': col.get('caption'),
                    'datatype': col.get('datatype'),
                    'role': col.get('role'),
                    'type': col.get('type'),
                    'hidden': col.get('hidden') == 'true'
                }
                
                # Check for calculation
                calc = col.find('calculation')
                if calc is not None:
                    column['calculation'] = calc.get('formula')
                    workbook['calculated_fields'].append({
                        'datasource': ds_caption,
                        'name': col.get('caption', col.get('name')),
                        'formula': calc.get('formula')
                    })
                
                datasource['columns'].append(column)
            
            workbook['datasources'].append(datasource)
    
    # Parse worksheets
    for ws in root.findall('.//worksheet'):
        worksheet = {
            'name': ws.get('name'),
            'datasources': [],
            'rows': None,
            'cols': None,
            'filters': [],
            'mark_type': None
        }
        
        # Datasources used
        for ds_ref in ws.findall('.//view/datasources/datasource'):
            worksheet['datasources'].append(ds_ref.get('name'))
        
        # Rows and columns shelves
        rows = ws.find('.//rows')
        cols = ws.find('.//cols')
        if rows is not None:
            worksheet['rows'] = rows.text
        if cols is not None:
            worksheet['cols'] = cols.text
        
        # Mark type
        mark = ws.find('.//mark')
        if mark is not None:
            worksheet['mark_type'] = mark.get('class')
        
        # Filters
        for f in ws.findall('.//filter'):
            worksheet['filters'].append({
                'class': f.get('class'),
                'column': f.get('column')
            })
        
        workbook['worksheets'].append(worksheet)
    
    # Parse dashboards
    for db in root.findall('.//dashboard'):
        dashboard = {
            'name': db.get('name'),
            'size': None,
            'worksheets': []
        }
        
        # Size
        size = db.find('size')
        if size is not None:
            dashboard['size'] = {
                'maxwidth': size.get('maxwidth'),
                'maxheight': size.get('maxheight'),
                'minwidth': size.get('minwidth'),
                'minheight': size.get('minheight')
            }
        
        # Worksheets in dashboard
        for zone in db.findall('.//zone[@type="worksheet"]'):
            dashboard['worksheets'].append(zone.get('name'))
        
        workbook['dashboards'].append(dashboard)
    
    return workbook


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_twb.py <workbook.twb|workbook.twbx>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        workbook = parse_workbook(file_path)
        print(json.dumps(workbook, indent=2))
    except Exception as e:
        print(f"Error parsing workbook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
