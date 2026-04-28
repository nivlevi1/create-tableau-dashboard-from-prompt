# Tableau Hyper API Reference

The Hyper API allows programmatic creation and manipulation of Tableau extract files (.hyper). Use it to:
- Create extracts for unsupported data sources
- Automate ETL processes with rolling updates
- Read data from existing extracts
- Perform incremental updates to published data sources

## Installation

```bash
pip install tableauhyperapi
```

**Requirements:** 64-bit platform (Windows, Linux, macOS)

## Basic Workflow

```python
from tableauhyperapi import (
    HyperProcess, Telemetry, Connection, CreateMode,
    TableDefinition, TableName, SqlType, Inserter
)

# 1. Start Hyper process (only one per application)
with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    
    # 2. Create/connect to .hyper file
    with Connection(
        endpoint=hyper.endpoint,
        database='mydata.hyper',
        create_mode=CreateMode.CREATE_AND_REPLACE
    ) as connection:
        
        # 3. Define table schema
        table_def = TableDefinition(
            table_name=TableName('Extract', 'Sales'),
            columns=[
                TableDefinition.Column('Order ID', SqlType.text(), NOT_NULLABLE),
                TableDefinition.Column('Region', SqlType.text()),
                TableDefinition.Column('Sales', SqlType.double()),
                TableDefinition.Column('Order Date', SqlType.date()),
            ]
        )
        
        # 4. Create table
        connection.catalog.create_schema('Extract')
        connection.catalog.create_table(table_def)
        
        # 5. Insert data
        with Inserter(connection, table_def) as inserter:
            inserter.add_row(['ORD-001', 'East', 1500.00, date(2025, 1, 15)])
            inserter.add_row(['ORD-002', 'West', 2300.50, date(2025, 1, 16)])
            inserter.execute()
```

## Data Types

| SqlType | Python Type | Description |
|---------|-------------|-------------|
| `SqlType.text()` | `str` | Variable-length string |
| `SqlType.int()` | `int` | 32-bit integer |
| `SqlType.big_int()` | `int` | 64-bit integer |
| `SqlType.small_int()` | `int` | 16-bit integer |
| `SqlType.double()` | `float` | 64-bit floating point |
| `SqlType.bool()` | `bool` | Boolean |
| `SqlType.date()` | `date` | Date without time |
| `SqlType.timestamp()` | `datetime` | Date with time |
| `SqlType.timestamp_tz()` | `datetime` | Timestamp with timezone |
| `SqlType.interval()` | `timedelta` | Time interval |
| `SqlType.geography()` | `bytes` | Geographic data (WKT/WKB) |
| `SqlType.bytes()` | `bytes` | Binary data |
| `SqlType.json()` | `str` | JSON text |
| `SqlType.oid()` | `int` | Object identifier |

### Nullability

```python
from tableauhyperapi import NOT_NULLABLE, NULLABLE

TableDefinition.Column('ID', SqlType.int(), NOT_NULLABLE)  # Required
TableDefinition.Column('Notes', SqlType.text(), NULLABLE)   # Optional (default)
```

## Table Definition

### Basic Table
```python
table_def = TableDefinition(
    table_name='Products',  # Simple name (uses default schema)
    columns=[
        TableDefinition.Column('Product ID', SqlType.int(), NOT_NULLABLE),
        TableDefinition.Column('Product Name', SqlType.text()),
        TableDefinition.Column('Price', SqlType.double()),
    ]
)
```

### With Schema
```python
table_def = TableDefinition(
    table_name=TableName('MySchema', 'Products'),
    columns=[...]
)

# Create schema first
connection.catalog.create_schema_if_not_exists('MySchema')
connection.catalog.create_table(table_def)
```

## Inserting Data

### Row-by-Row
```python
with Inserter(connection, table_def) as inserter:
    for row in data:
        inserter.add_row([row['id'], row['name'], row['value']])
    inserter.execute()
```

### Bulk Insert (Better Performance)
```python
with Inserter(connection, table_def) as inserter:
    inserter.add_rows([
        ['ORD-001', 'East', 1500.00],
        ['ORD-002', 'West', 2300.50],
        ['ORD-003', 'North', 800.25],
    ])
    inserter.execute()
```

### From Pandas DataFrame
```python
import pantab  # pip install pantab

import pandas as pd

df = pd.DataFrame({
    'Order ID': ['ORD-001', 'ORD-002'],
    'Region': ['East', 'West'],
    'Sales': [1500.00, 2300.50]
})

# Write DataFrame to Hyper
pantab.frame_to_hyper(df, 'output.hyper', table='Sales')

# Read Hyper to DataFrame
df = pantab.frame_from_hyper('output.hyper', table='Sales')
```

### From CSV (High Performance)
```python
# Use SQL COPY for best performance with large CSV files
copy_command = f"""
    COPY "Extract"."Sales" FROM '{csv_path}'
    WITH (FORMAT csv, HEADER true, DELIMITER ',')
"""
connection.execute_command(copy_command)
```

## Reading Data

### Execute Query
```python
# Get all rows
with connection.execute_query('SELECT * FROM "Extract"."Sales"') as result:
    for row in result:
        print(row[0], row[1], row[2])  # Access by index

# With column names
with connection.execute_query('SELECT * FROM "Extract"."Sales"') as result:
    columns = [col.name for col in result.schema.columns]
    for row in result:
        print(dict(zip(columns, row)))
```

### Aggregate Queries
```python
query = '''
    SELECT "Region", SUM("Sales") as TotalSales
    FROM "Extract"."Sales"
    GROUP BY "Region"
    ORDER BY TotalSales DESC
'''
with connection.execute_query(query) as result:
    for row in result:
        print(f"{row[0]}: ${row[1]:,.2f}")
```

### Scalar Query
```python
row_count = connection.execute_scalar_query(
    'SELECT COUNT(*) FROM "Extract"."Sales"'
)
print(f"Total rows: {row_count}")
```

## Updating Data

### SQL UPDATE
```python
connection.execute_command('''
    UPDATE "Extract"."Sales"
    SET "Sales" = "Sales" * 1.1
    WHERE "Region" = 'West'
''')
```

### SQL DELETE
```python
connection.execute_command('''
    DELETE FROM "Extract"."Sales"
    WHERE "Order Date" < '2024-01-01'
''')
```

### Upsert Pattern
```python
# Create temp table, insert new data, merge
connection.execute_command('''
    CREATE TEMPORARY TABLE temp_sales AS 
    SELECT * FROM "Extract"."Sales" WHERE FALSE
''')

# Insert new/updated rows to temp
with Inserter(connection, TableName('temp_sales')) as inserter:
    inserter.add_rows(new_data)
    inserter.execute()

# Merge: Update existing, insert new
connection.execute_command('''
    MERGE INTO "Extract"."Sales" AS target
    USING temp_sales AS source
    ON target."Order ID" = source."Order ID"
    WHEN MATCHED THEN UPDATE SET 
        "Sales" = source."Sales",
        "Region" = source."Region"
    WHEN NOT MATCHED THEN INSERT VALUES (
        source."Order ID", source."Region", source."Sales", source."Order Date"
    )
''')
```

## Multi-Table Extracts

```python
# Create multiple related tables
customers_def = TableDefinition(
    table_name=TableName('Extract', 'Customers'),
    columns=[
        TableDefinition.Column('Customer ID', SqlType.int(), NOT_NULLABLE),
        TableDefinition.Column('Customer Name', SqlType.text()),
    ]
)

orders_def = TableDefinition(
    table_name=TableName('Extract', 'Orders'),
    columns=[
        TableDefinition.Column('Order ID', SqlType.int(), NOT_NULLABLE),
        TableDefinition.Column('Customer ID', SqlType.int()),  # FK
        TableDefinition.Column('Amount', SqlType.double()),
    ]
)

connection.catalog.create_table(customers_def)
connection.catalog.create_table(orders_def)
```

## Working with Existing Files

### Open Existing
```python
with Connection(
    endpoint=hyper.endpoint,
    database='existing.hyper',
    create_mode=CreateMode.NONE  # Don't create, error if missing
) as connection:
    # Read or modify data
    pass
```

### Create If Not Exists
```python
with Connection(
    endpoint=hyper.endpoint,
    database='data.hyper',
    create_mode=CreateMode.CREATE_IF_NOT_EXISTS
) as connection:
    # Creates file if missing, opens if exists
    pass
```

### Get Table Info
```python
# List all tables
tables = connection.catalog.get_table_names('Extract')
print(tables)  # [TableName('Extract', 'Sales'), ...]

# Get table definition
table_def = connection.catalog.get_table_definition(
    TableName('Extract', 'Sales')
)
for col in table_def.columns:
    print(f"{col.name}: {col.type}")
```

## Performance Tips

### 1. Use Correct Data Types
```python
# GOOD: Use native types
TableDefinition.Column('Amount', SqlType.double())
TableDefinition.Column('Order Date', SqlType.date())

# BAD: Everything as text (slow)
TableDefinition.Column('Amount', SqlType.text())  # Don't do this
```

### 2. Batch Inserts
```python
# GOOD: Batch rows
with Inserter(connection, table_def) as inserter:
    inserter.add_rows(all_rows)  # Add all at once
    inserter.execute()

# BAD: Row-by-row with execute each time
for row in all_rows:
    with Inserter(connection, table_def) as inserter:
        inserter.add_row(row)
        inserter.execute()  # Don't do this
```

### 3. Use COPY for CSV
```python
# Fastest way to load CSV
connection.execute_command(f'''
    COPY "Extract"."Data" FROM '{csv_path}'
    WITH (FORMAT csv, HEADER true)
''')
```

### 4. Allocate Sufficient Memory
The Hyper process needs RAM for intermediate results. Large datasets may require more memory than default.

### 5. Consider Language Choice
For heavy insert/read operations:
- C++ is fastest
- Python is slowest (but most convenient)
- Consider using `pantab` for DataFrame workflows

## Publishing to Tableau Server

After creating a .hyper file, publish it using the REST API:

```python
import tableauserverclient as TSC

# Connect to server
auth = TSC.PersonalAccessTokenAuth('token-name', 'secret', 'site')
server = TSC.Server('https://server.com', use_server_version=True)

with server.auth.sign_in(auth):
    # Publish as data source
    ds = TSC.DatasourceItem(project_id='project-id', name='My Data')
    ds = server.datasources.publish(
        ds, 
        'mydata.hyper',
        mode=TSC.Server.PublishMode.Overwrite
    )
    print(f"Published: {ds.id}")
```

### Incremental Update (Append/Replace)
```python
# Update existing published data source
server.datasources.update_hyper_data(
    datasource_id='datasource-id',
    request_id='unique-request-id',
    actions=[
        {
            "action": "insert",
            "source-table": "Sales",
            "target-table": "Sales",
            "source-schema": "Extract"
        }
    ],
    payload='new_data.hyper'
)
```

## Complete Example: ETL Pipeline

```python
from tableauhyperapi import (
    HyperProcess, Telemetry, Connection, CreateMode,
    TableDefinition, TableName, SqlType, Inserter, NOT_NULLABLE
)
import tableauserverclient as TSC
import pandas as pd
from datetime import date

def create_sales_extract(data: pd.DataFrame, output_path: str):
    """Create .hyper extract from DataFrame."""
    
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint,
            database=output_path,
            create_mode=CreateMode.CREATE_AND_REPLACE
        ) as connection:
            
            # Define schema
            table_def = TableDefinition(
                table_name=TableName('Extract', 'Sales'),
                columns=[
                    TableDefinition.Column('Order ID', SqlType.text(), NOT_NULLABLE),
                    TableDefinition.Column('Customer', SqlType.text()),
                    TableDefinition.Column('Product', SqlType.text()),
                    TableDefinition.Column('Region', SqlType.text()),
                    TableDefinition.Column('Sales', SqlType.double()),
                    TableDefinition.Column('Quantity', SqlType.int()),
                    TableDefinition.Column('Order Date', SqlType.date()),
                ]
            )
            
            connection.catalog.create_schema('Extract')
            connection.catalog.create_table(table_def)
            
            # Insert data
            with Inserter(connection, table_def) as inserter:
                for _, row in data.iterrows():
                    inserter.add_row([
                        row['order_id'],
                        row['customer'],
                        row['product'],
                        row['region'],
                        float(row['sales']),
                        int(row['quantity']),
                        row['order_date']
                    ])
                inserter.execute()
            
            # Verify
            count = connection.execute_scalar_query(
                'SELECT COUNT(*) FROM "Extract"."Sales"'
            )
            print(f"Created extract with {count} rows")


def publish_to_server(hyper_path: str, server_url: str, 
                      token_name: str, token_secret: str,
                      site: str, project_id: str):
    """Publish .hyper file to Tableau Server/Cloud."""
    
    auth = TSC.PersonalAccessTokenAuth(token_name, token_secret, site)
    server = TSC.Server(server_url, use_server_version=True)
    
    with server.auth.sign_in(auth):
        ds = TSC.DatasourceItem(project_id=project_id, name='Sales Extract')
        ds = server.datasources.publish(
            ds, 
            hyper_path,
            mode=TSC.Server.PublishMode.Overwrite
        )
        print(f"Published datasource: {ds.id}")
        return ds.id


# Example usage
if __name__ == '__main__':
    # Sample data
    df = pd.DataFrame({
        'order_id': ['ORD-001', 'ORD-002', 'ORD-003'],
        'customer': ['Acme Corp', 'Global Inc', 'Tech Ltd'],
        'product': ['Widget A', 'Widget B', 'Widget A'],
        'region': ['East', 'West', 'North'],
        'sales': [1500.00, 2300.50, 800.25],
        'quantity': [10, 15, 5],
        'order_date': [date(2025, 1, 15), date(2025, 1, 16), date(2025, 1, 17)]
    })
    
    # Create extract
    create_sales_extract(df, 'sales_extract.hyper')
    
    # Publish to server (uncomment with real credentials)
    # publish_to_server(
    #     'sales_extract.hyper',
    #     'https://10ax.online.tableau.com',
    #     'my-token', 'my-secret',
    #     'my-site', 'project-id'
    # )
```

## Resources

- **Official Documentation:** https://tableau.github.io/hyper-db/docs/
- **Python Reference:** https://tableau.github.io/hyper-db/lang_docs/py/
- **Sample Code:** https://github.com/tableau/hyper-api-samples
- **Pantab (DataFrame integration):** https://pantab.readthedocs.io/
- **PyPI Package:** https://pypi.org/project/tableauhyperapi/
