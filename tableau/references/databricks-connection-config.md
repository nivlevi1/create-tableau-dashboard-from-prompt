# Databricks Connection Configuration for Tableau TWB Generation

Use these values when generating direct (federated) Databricks connections in TWB files.

## Connection Parameters

| Parameter | Value |
|-----------|-------|
| **Server** | `dbc-2e4dd055-1953.cloud.databricks.com` |
| **Catalog (dbname)** | `analytics-nexus-prod` |
| **Default Schema** | `marts` |
| **Warehouse HTTP Path** | `/sql/1.0/warehouses/e4f76e7a613ebb69` |
| **Authentication** | `auth-pass` (PAT — user prompted at runtime) |
| **Workgroup Auth Mode** | `prompt` |

## XML Template

```xml
<named-connection caption='dbc-2e4dd055-1953.cloud.databricks.com'
                  name='databricks.<unique_id>'>
  <connection authentication='auth-pass'
              authentication-type=''
              class='databricks'
              dbname='analytics-nexus-prod'
              odbc-connect-string-extras=''
              one-time-sql=''
              schema='marts'
              server='dbc-2e4dd055-1953.cloud.databricks.com'
              server-oauth=''
              username=''
              v-http-path='/sql/1.0/warehouses/e4f76e7a613ebb69'
              workgroup-auth-mode='prompt' />
</named-connection>
```

## Python Template

```python
DATABRICKS_SERVER = "dbc-2e4dd055-1953.cloud.databricks.com"
WAREHOUSE_PATH = "/sql/1.0/warehouses/e4f76e7a613ebb69"
CATALOG = "analytics-nexus-prod"
SCHEMA = "marts"
```

## Source

Extracted from production dashboards: `arr_dashboard.twb`, `daily_sales_dashboard.twb`, `yesterday_sales_v2.twb`.
