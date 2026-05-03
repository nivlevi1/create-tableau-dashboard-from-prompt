# Tableau Data Source Connections

Authoritative reference for Tableau TWB data source connections: published (`sqlproxy`) and direct (`federated`). Cross-check validated workbook rules in [programmatic-twb-learnings.md](programmatic-twb-learnings.md) (especially **§1** root/manifest, **§2** datasource order and metadata, **§3** formula encoding). For troubleshooting load/publish errors, see [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md) (e.g. internal error `018B7D29` when Custom SQL lacks `metadata-records`).

---

## Two Connection Patterns

| Aspect | Published (`sqlproxy`) | Direct (`federated`) |
|--------|------------------------|----------------------|
| **Connection class** | `class='sqlproxy'` (Tableau Server/Cloud data server) | `class='federated'` wrapping inner `class='databricks'` (or other DB) |
| **Datasource `name`** | `sqlproxy.<id>` | `federated.<id>` |
| **Data governance** | Centralized on Tableau Server/Cloud | Each workbook embeds its own connection |
| **Custom SQL** | Not in the workbook (use published DS fields) | Embedded (`relation type='text'`) |
| **Flexibility** | Limited to what the published DS exposes | Any table/view/SQL the DB allows |
| **Typical use** | Production, governed dashboards | Ad-hoc SQL, prototyping, extra queries |
| **Requires Tableau Server** | Yes (DS must exist on server) | No (Desktop can open with credentials) |
| **`<repository-location>`** | Yes | No |
| **`<named-connections>`** | No | Yes |
| **`connection-customization`** | No | Omit when generating programmatically; Desktop-saved files often include it |
| **`<relation type='text'>` (Custom SQL)** | No | Yes |
| **`<calculations>` inside connection** | Yes (calcs on published DS) | No (calcs live under datasource `<column>`) |
| **`metadata-records`** | Optional; may appear for calculated columns on published DS | **Required** for Custom SQL in generated TWBs; recommended for table relations |

A single workbook may mix both (e.g. `sqlproxy` for a Revenue published source plus `federated` for Custom SQL against Databricks).

---

## Published Data Source (sqlproxy)

### XML pattern

Published connections point at a server-hosted data source. The workbook stays lightweight (no embedded DB connection).

```xml
<datasource caption='Sales Data (Published)' inline='true'
            name='sqlproxy.1rfw7xb1xv29kt1cv7fne0cre0xx' version='18.1'>

  <repository-location derived-from='http://your-pod.online.tableau.com/t/site/datasources/SalesData?rev=1.2'
                       id='SalesData' path='/t/site/datasources' revision='1.3'
                       site='YourSiteName' />

  <connection channel='https' class='sqlproxy' dbname='SalesData'
              directory='/dataserver' local-dataserver='' port='443'
              server='your-pod.online.tableau.com'
              server-ds-friendly-name='Sales Data (Published)'
              server-oauth='' username='' workgroup-auth-mode='prompt'>

    <relation type='collection'>
      <relation connection='sqlproxy.1rfw7xb1xv29kt1cv7fne0cre0xx' name='sqlproxy' table='[sqlproxy]' type='table' />
    </relation>

    <calculations>
      <calculation column='[Total Revenue]' formula='SUM([Sales]) + SUM([Profit])' />
    </calculations>
  </connection>

  <column datatype='string' name='[Region]' role='dimension' type='nominal' />
  <column datatype='real' name='[Sales]' role='measure' type='quantitative' />
</datasource>
```

**`repository-location`**

```xml
<repository-location derived-from='http://server.com/t/site/datasources/DataSourceName?rev=1.0'
                     id='DataSourceName' path='/t/site/datasources' revision='1.3' site='SiteName' />
```

- `id`: Published data source name (must match `dbname` on the connection).
- `path`: Often `/t/{site}/datasources` on Tableau Cloud; `/datasources` appears in simpler samples.
- `revision`: DS version (e.g. `1.3`, `4.6`).
- `site`: Site name for multi-site or Cloud.
- `derived-from`: Optional reference URL.

**`connection` (`class='sqlproxy'`)**

- `server`: Tableau Cloud pod or Server hostname.
- `channel`: `https` for Cloud.
- `directory`: `/dataserver`.
- `dbname`: Same as published DS name / `repository-location` `id`.
- `workgroup-auth-mode`: e.g. `prompt`, `as-is`, or empty.

**Collection relation**

Real workbooks often nest the proxy table:

```xml
<relation type='collection'>
  <relation connection='sqlproxy.1rfw7xb1xv29kt1cv7fne0cre0xx' name='sqlproxy' table='[sqlproxy]' type='table' />
</relation>
```

Inner `connection` on the nested `relation` should match the datasource `name` when present.

### `<calculations>` on published data sources

Define calculated fields at the connection level; escape XML in formulas (`&gt;`, `&lt;`, `&apos;`, `&quot;`).

```xml
<calculations>
  <calculation column='[ROI]'
    formula='IF sum([total_spend])&gt;0 and SUM([new_revenue_completed_hosting_plugin])&gt;0 then sum([new_revenue_completed_hosting_plugin])/SUM([total_spend]) END' />
</calculations>
```

### `metadata-records` on sqlproxy (optional)

Published datasources **may** include `metadata-records` (e.g. for layered calculated measures). Example shape from production:

```xml
<metadata-records>
  <metadata-record class='measure'>
    <remote-name>ROI</remote-name>
    <remote-type>-1</remote-type>
    <local-name>[ROI]</local-name>
    <parent-name>[sqlproxy]</parent-name>
    <remote-alias>ROI</remote-alias>
    <ordinal>25</ordinal>
    <layered>true</layered>
    <caption>ROI</caption>
    <local-type>real</local-type>
    <aggregation>User</aggregation>
    <contains-null>true</contains-null>
    <attributes>
      <attribute datatype='integer' name='field-type'>0</attribute>
      <attribute datatype='string' name='formula'>"IF sum([total_spend])&gt;0..."</attribute>
    </attributes>
  </metadata-record>
</metadata-records>
```

### Discovery: REST API, MCP, browser URL

**REST (tableauserverclient)**

```python
import tableauserverclient as TSC

tableau_auth = TSC.PersonalAccessTokenAuth(
    'your-pat-name', 'your-pat-secret', 'your-site-name'
)
server = TSC.Server('https://prod-useast-a.online.tableau.com', use_server_version=True)

with server.auth.sign_in(tableau_auth):
    all_datasources, pagination = server.datasources.get()
    for ds in all_datasources:
        print(f"Name: {ds.name}")
        print(f"ID (LUID): {ds.id}")
        print(f"Content URL: {ds.content_url}")
```

**Information for the TWB**

| Attribute | Source | Example |
|-----------|--------|---------|
| `server` | Cloud pod / Server host | `prod-useast-a.online.tableau.com` |
| `site` | Site name | `MyCompanySite` |
| `dbname` / `id` | Published DS name | `Superstore` |

**Tableau MCP** (when enabled): e.g. list datasources, `get-datasource-metadata` by LUID, search by name — use these to avoid manual copy/paste of names, IDs, and columns.

**Browser**: Published DS URLs resemble  
`https://<host>/t/<site>/datasources/<name>` — useful for `derived-from` and confirming site/path.

### Publish workflow: authenticate → get DS info → generate TWB → publish

1. **Authenticate** with PAT (or other supported auth) and **resolve** the published data source (name, site, server, revision if needed).
2. **Generate** the workbook XML with matching `repository-location`, `sqlproxy` connection, collection relation, and `<column>` definitions aligned to the published fields.
3. **Publish** with `skip_connection_check=True` for sqlproxy to avoid unnecessary connection validation failures.

```python
def publish_workbook(server_url, site_name, pat_name, pat_secret,
                     workbook_path, project_name):
    import tableauserverclient as TSC
    tableau_auth = TSC.PersonalAccessTokenAuth(pat_name, pat_secret, site_name)
    server = TSC.Server(server_url, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        all_projects, _ = server.projects.get()
        project = next((p for p in all_projects if p.name == project_name), None)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        workbook_item = TSC.WorkbookItem(project.id)
        workbook_item = server.workbooks.publish(
            workbook_item,
            workbook_path,
            mode=TSC.Server.PublishMode.Overwrite,
            skip_connection_check=True,
        )
        return workbook_item
```

`tableaudocumentapi` does not create workbooks from scratch; for new files, build XML directly (see **Python Generation Template**).

---

## Direct Database Connection (federated)

Direct connections use a **federated** wrapper around **named-connections** (inner DB connector).

### Federated wrapper structure

```
<datasource name='federated.<id>'>
  └── <connection class='federated'>
        ├── <named-connections>
        │     └── <named-connection name='databricks.<id>'>
        │           └── <connection class='databricks' ... />
        ├── <relation ... />          <!-- table or Custom SQL -->
        └── <metadata-records>        <!-- required for Custom SQL in generated TWBs -->
```

Complete Databricks example (production-style; inner connection uses `v-http-path`):

```xml
<datasource caption='new_paid_users_ytd(prep)' inline='true'
            name='federated.02bm58x14zgdy9188vvi70n3vz3a' version='18.1'>
  <connection class='federated'>
    <named-connections>
      <named-connection caption='dbc-XXXX.cloud.databricks.com'
                        name='databricks.0fy96ry16x2arq100fydu0fmm2qe'>
        <connection authentication='auth-pass'
                    authentication-type=''
                    class='databricks'
                    dbname='your-catalog'
                    odbc-connect-string-extras=''
                    one-time-sql=''
                    schema='marts'
                    server='dbc-XXXX.cloud.databricks.com'
                    server-oauth=''
                    server-userid='000000'
                    username=''
                    v-http-path='/sql/1.0/warehouses/WAREHOUSE_ID'
                    workgroup-auth-mode='prompt'>
          <connection-customization class='databricks' enabled='false' version='18.1'>
            <vendor name='databricks' />
            <driver name='databricks' />
            <customizations>
              <customization name='CAP_ODBC_CURSOR_FORWARD_ONLY' value='yes' />
              <!-- … full list in § Databricks Connection-Customization -->
            </customizations>
          </connection-customization>
        </connection>
      </named-connection>
    </named-connections>

    <relation connection='databricks.0fy96ry16x2arq100fydu0fmm2qe'
             name='Custom SQL Query' type='text'>WITH monthly_goals AS(
    SELECT  *
    FROM `your-catalog`.`marts`.`monthly_goals`
    WHERE product_name = &quot;All Products&quot;
    AND measurement = &quot;users&quot;
    AND action = &apos;NEW&apos;
)
SELECT  a.*, m.goal AS monthly_goal
FROM `your-catalog`.`prep`.`new_paid_users_ytd` a
LEFT JOIN monthly_goals m
ON DATE_TRUNC(&apos;month&apos;,a.date_in_year)::DATE = m.month</relation>

    <metadata-records>
      <metadata-record class='column'>
        <remote-name>day_of_year</remote-name>
        <remote-type>3</remote-type>
        <local-name>[day_of_year]</local-name>
        <parent-name>[Custom SQL Query]</parent-name>
        <remote-alias>day_of_year</remote-alias>
        <ordinal>1</ordinal>
        <local-type>integer</local-type>
        <aggregation>Sum</aggregation>
        <precision>10</precision>
        <contains-null>true</contains-null>
        <attributes>
          <attribute datatype='string' name='DebugRemoteType'>&quot;SQL_INTEGER&quot;</attribute>
          <attribute datatype='string' name='DebugWireType'>&quot;SQL_C_SLONG&quot;</attribute>
        </attributes>
      </metadata-record>
    </metadata-records>
  </connection>
  <aliases enabled='yes' />
  <column caption='Cumulative Current Year' datatype='integer'
          name='[cumulative_current_year]' role='measure' type='quantitative' />
</datasource>
```

**Programmatic generation:** omit `<connection-customization>` (see [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §2). Desktop-saved workbooks often retain it with `enabled='false'`.

### Custom SQL: `relation type="text"`

Use `connection` pointing at the named-connection id. Prefer CDATA for large or quote-heavy SQL; otherwise XML-encode.

**CDATA**

```xml
<relation connection='databricks.<id>' name='Custom SQL Query' type='text'>
<![CDATA[
  WITH daily_dates AS (
      SELECT DISTINCT date
      FROM `your-catalog`.marts.dim_calendar
      WHERE date < CURRENT_DATE
  )
  SELECT d.date, COUNT(DISTINCT u.user_id) AS active_users
  FROM daily_dates d
  LEFT JOIN qualified_users u ON ...
  GROUP BY d.date
]]></relation>
```

**Inline (entity-encoded)**

```xml
<relation connection='databricks.<id>' name='Custom SQL Query' type='text'>SELECT *
FROM `your-catalog`.`marts`.`order_items_status`
WHERE order_status = &apos;COMPLETED&apos;</relation>
```

**Parameter marker caveat**: A raw `<` in SQL (e.g. `WHERE col < 1`) must be written as `&lt;` in non-CDATA XML so it is not parsed as a tag.

### `metadata-records` (Custom SQL and tables)

Describe columns returned by the database. Tableau Desktop generates these automatically; for **programmatic** TWBs, include them for Custom SQL to avoid errors and extra metadata round-trips (see [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §2 and [error-codes-and-pitfalls.md](error-codes-and-pitfalls.md) for `018B7D29`).

```xml
<metadata-record class='column'>
  <remote-name>column_name</remote-name>
  <remote-type>3</remote-type>
  <local-name>[column_name]</local-name>
  <parent-name>[Custom SQL Query]</parent-name>
  <remote-alias>column_name</remote-alias>
  <ordinal>1</ordinal>
  <local-type>integer</local-type>
  <aggregation>Sum</aggregation>
  <precision>10</precision>
  <contains-null>true</contains-null>
  <attributes>
    <attribute datatype='string' name='DebugRemoteType'>&quot;SQL_INTEGER&quot;</attribute>
    <attribute datatype='string' name='DebugWireType'>&quot;SQL_C_SLONG&quot;</attribute>
  </attributes>
</metadata-record>
```

**ODBC type codes (`remote-type`) — common mappings**

| Code | ODBC type | Tableau `local-type` | Default aggregation |
|------|-----------|----------------------|----------------------|
| 3 | SQL_INTEGER | integer | Sum |
| 5 | SQL_DOUBLE | real | Sum |
| 7 | SQL_TYPE_DATE / TIMESTAMP | date / datetime | Year |
| 12 | SQL_VARCHAR | string | Count |
| 20 | SQL_BIGINT | integer | Sum |

String columns may also include `<width>`, `<collation>`, and `TypeIsVarchar` attributes.

### Table references: `relation type="table"`

```xml
<relation connection='databricks.<id>'
         name='order_items_status'
         table='[your-catalog].[marts].[order_items_status]'
         type='table' />
```

**Multiple tables (collection)**

```xml
<relation type='collection'>
  <relation connection='databricks.<id>'
           name='orders' table='[catalog].[schema].[orders]' type='table' />
  <relation connection='databricks.<id>'
           name='users' table='[catalog].[schema].[users]' type='table' />
</relation>
```

### Object graph (Custom SQL)

Custom SQL workbooks may include `<object-graph>` repeating the query for Tableau’s internal model. It is auto-generated; optional for minimal programmatic TWBs — Tableau can rebuild it.

---

### When to include `metadata-records`

| Scenario | Include `metadata-records`? |
|----------|----------------------------|
| **Federated Custom SQL** (`type='text'`) in generated TWBs | **Required** — avoids internal errors and matches [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §2 |
| **Federated table** (`type='table'`) | Recommended; Tableau can discover types if omitted |
| **Published `sqlproxy`** | **Optional** — often omitted; **may** be present for calculated fields on the published DS (e.g. `class='measure'`, `parent-name='[sqlproxy]'`) |

---

## Databricks Connection Attributes

Use **`v-http-path`** for the SQL warehouse HTTP path (e.g. `/sql/1.0/warehouses/<id>`).

| Attribute | Role |
|-----------|------|
| `class` | `databricks` |
| `server` | Workspace hostname |
| `dbname` | Unity Catalog name |
| `schema` | Default schema |
| `v-http-path` | Warehouse path |
| `authentication` | e.g. `auth-pass` (PAT), `OAuth` |
| `workgroup-auth-mode` | e.g. `prompt` for runtime credentials |
| `one-time-sql` | Optional initial SQL |
| `odbc-connect-string-extras` | Extra ODBC parameters |
| `server-userid` | Optional cached credential viewer id |

**Org-specific values** (actual server, catalog, warehouse path): see **[databricks-connection-config.md](databricks-connection-config.md)**.

**`connection-customization`**: **Omit when generating TWB XML programmatically.** Keep in samples from Desktop saves for fidelity; programmatic generation should follow [programmatic-twb-learnings.md](programmatic-twb-learnings.md) §2.

### Databricks connection-customization (full capability list)

Present in many Desktop exports; when omitted programmatically, the driver defaults apply. Full flag list for reference:

| Capability | Description |
|------------|-------------|
| `CAP_AUTH_KERBEROS_IMPERSONATE` | Kerberos impersonation support |
| `CAP_ODBC_CURSOR_FORWARD_ONLY` | Forward-only cursor |
| `CAP_ODBC_FETCH_INT_TRUNCATION_AS_ERROR` | Int truncation as error |
| `CAP_ODBC_UNBIND_EACH` | Unbind after each fetch |
| `CAP_ODBC_USE_NATIVE_PROTOCOL` | Native ODBC protocol |
| `CAP_QUERY_ALLOW_JOIN_REORDER` | Join reordering |
| `CAP_QUERY_ALLOW_PARTIAL_AGGREGATION` | Partial aggregation |
| `CAP_QUERY_GROUP_BY_ALIAS` | GROUP BY alias |
| `CAP_QUERY_GROUP_BY_DEGREE` | GROUP BY ordinal |
| `CAP_QUERY_HAVING_REQUIRES_GROUP_BY` | HAVING requires GROUP BY |
| `CAP_QUERY_INLINE_COMPLEX_GROUPBYS_IN_SELECTS` | Inline complex GROUP BY |
| `CAP_QUERY_JOIN_ACROSS_SCHEMAS` | Cross-schema joins |
| `CAP_QUERY_NULL_REQUIRES_CAST` | NULL needs CAST |
| `CAP_QUERY_SORT_BY` | ORDER BY |
| `CAP_QUERY_SUBQUERIES` | Subqueries |
| `CAP_QUERY_SUBQUERIES_WITH_TOP` | Subqueries with LIMIT |
| `CAP_QUERY_SUBQUERY_QUERY_CONTEXT` | Subquery context |
| `CAP_QUERY_SUPPORTS_LODJOINS` | LOD expression joins |
| `CAP_QUERY_SUPPORT_ANALYTIC_FUNCTIONS` | Window functions |
| `CAP_QUERY_TOP_0_METADATA` | TOP 0 for metadata |
| `CAP_QUERY_TOP_N` | LIMIT |
| `CAP_QUERY_USE_DOMAIN_RANGES_OPTIMIZATION` | Domain range optimization |
| `CAP_QUERY_USE_QUERY_FUSION` | Query fusion |
| `CAP_SUPPRESS_CONNECTION_POOLING` | Disable connection pooling |
| `CAP_SUPPRESS_ENUMERATE_SCHEMAS_VIA_SQL` | Skip schema enumeration |
| `CAP_SUPPRESS_ENUMERATE_TABLES_VIA_SQL` | Skip table enumeration |
| `CAP_SUPPRESS_GET_SERVER_TIME` | Skip server time |
| `CAP_ODBC_METADATA_SUPPRESS_SQLSTATISTICS_API` | Skip statistics API |
| `CAP_QUERY_BLENDING_PREFER_LOCAL_MAPPING_TABLES` | Local blending preference |
| `CAP_QUERY_BLENDING_REMOTE_MAPPING_TABLES` | Remote blending |

---

## Other Database Connectors

Inner connection examples (wrap in federated `named-connections` when used as direct connections). See **Two Connection Patterns** for wrapper structure.

### Excel

Minimal `excel-direct` (validated pattern):

```xml
<datasource caption="Sample - Superstore" inline="true"
            name="excel-direct.0s0w8bc1mmgszd1bpjkml0ajtnjl" version="18.1">
  <connection class="excel-direct" cleaning="no" compat="no"
              dataRefreshTime="" filename="/path/to/file.xls"
              interpretationMode="0" password="" server="" validate="no">
    <relation connection="excel-direct.0s0w8bc1mmgszd1bpjkml0ajtnjl"
              name="Orders" table="[Orders$]" type="table"/>
  </connection>
  <aliases enabled="yes"/>
</datasource>
```

- No `repository-location`.
- `relation` is a direct child of `connection`; `connection` on `relation` matches datasource `name`.
- Sheet: `[SheetName$]`.

With explicit columns:

```xml
<connection class='excel-direct' cleaning='no' compat='no'
            filename='/path/to/workbook.xlsx' validate='no'>
  <relation name='Sheet1' table='[Sheet1$]' type='table'>
    <columns gridOrigin='A1:D100:no:A1:D100:0' header='yes' outcome='6'>
      <column datatype='string' name='Name' ordinal='0' />
      <column datatype='integer' name='Value' ordinal='1' />
    </columns>
  </relation>
</connection>
```

### CSV / Text Files

```xml
<connection class='textscan' directory='/path/to/folder' filename='data.csv'
            password='' server=''>
  <relation name='data#csv' table='[data#csv]' type='table'>
    <columns header='yes' outcome='2'>
      <column datatype='string' name='F1' ordinal='0' />
    </columns>
  </relation>
</connection>
```

### SQL Server

```xml
<connection authentication='sqlserver' class='sqlserver'
            dbname='DatabaseName' odbc-native-protocol='yes'
            one-time-sql='' port='1433' server='server.database.windows.net'
            username='user@domain'>
  <relation name='TableName' table='[dbo].[TableName]' type='table' />
</connection>
```

### PostgreSQL

```xml
<connection class='postgres' dbname='database_name'
            one-time-sql='' port='5432' server='hostname'
            sslmode='require' username='postgres_user'>
  <relation name='public.tablename' table='[public].[tablename]' type='table' />
</connection>
```

### MySQL

```xml
<connection class='mysql' dbname='database_name'
            one-time-sql='' port='3306' server='mysql.server.com'
            username='mysql_user'>
  <relation name='tablename' table='[tablename]' type='table' />
</connection>
```

### Snowflake

```xml
<connection class='snowflake' dbname='DATABASE_NAME'
            one-time-sql='' port='443' schema='PUBLIC'
            server='account.snowflakecomputing.com'
            service='https://account.snowflakecomputing.com:443'
            warehouse='WAREHOUSE_NAME' username='SNOWFLAKE_USER'>
  <relation name='TABLE_NAME' table='[TABLE_NAME]' type='table' />
</connection>
```

### Amazon Redshift

```xml
<connection class='redshift' dbname='dev'
            odbc-connect-string-extras='' one-time-sql=''
            port='5439' schema='public'
            server='cluster.region.redshift.amazonaws.com'
            username='awsuser'>
  <relation name='tablename' table='[public].[tablename]' type='table' />
</connection>
```

### Google BigQuery

```xml
<connection class='bigquery' project='project-id'
            service-account-email='service@project.iam.gserviceaccount.com'>
  <relation name='dataset.tablename' table='[dataset].[tablename]' type='table' />
</connection>
```

### Hyper Extract (local)

```xml
<connection class='hyper' dbname='/path/to/extract.hyper'
            default-settings='yes' schema='Extract' sslmode=''
            tablename='Extract' username='tableau_internal_user'>
  <relation name='Extract' table='[Extract].[Extract]' type='table' />
</connection>
```

### Generic ODBC

```xml
<connection class='genericodbc' dbname='database'
            odbc-connect-string-extras='Driver={ODBC Driver};'
            odbc-driver='DriverName' odbc-native-protocol=''
            one-time-sql='' port='' schema='' server='hostname'
            username='user'>
</connection>
```

### Generic JDBC

```xml
<connection class='genericjdbc' dbname='database'
            jdbcurl='jdbc:driver://host:port/database'
            one-time-sql='' port='' schema='' server=''
            username='user'>
</connection>
```

### Named connection (reusable)

```xml
<named-connection caption='MyDatabase' name='connection.abc123'>
  <connection class='sqlserver' dbname='MyDB' server='server.com' ... />
</named-connection>
```

```xml
<relation connection='connection.abc123' name='TableName' ... />
```

---

## Connection Attributes Reference

| Attribute | Description |
|-----------|-------------|
| `class` | Connector identifier |
| `dbname` | Database / catalog name |
| `server` | Hostname or address |
| `port` | Port |
| `schema` | Schema (optional) |
| `username` | User (often empty when prompting) |
| `password` | Usually omitted or encrypted |
| `one-time-sql` | Initial SQL on connect |
| `odbc-connect-string-extras` | Extra ODBC parameters |
| `authentication` | Auth method (connector-specific) |
| `sslmode` | SSL mode (e.g. Postgres) |

---

## Custom SQL Query

```xml
<relation connection='connection.abc123' name='Custom SQL Query' type='text'>
  SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    o.order_date,
    o.amount
  FROM orders o
  JOIN customers c ON o.customer_id = c.id
  WHERE o.status = 'completed'
</relation>
```

- Use **CDATA** or entity encoding for quotes and `<`.
- **`<` in SQL** must not appear as a raw tag opener in non-CDATA XML — use `&lt;` or CDATA.

---

## Initial SQL

Set on the connection via `one-time-sql`:

```xml
<connection class='postgres' ... one-time-sql='SET search_path TO myschema;'>
```

---

## Multiple Tables (Union)

```xml
<relation name='Union' type='union'>
  <columns>
    <column datatype='string' name='[City]' />
    <column datatype='integer' name='[Sales]' />
  </columns>
  <relation name='Table1' table='[Table1]' type='table' />
  <relation name='Table2' table='[Table2]' type='table' />
</relation>
```

---

## Authentication Methods

| Connection | Auth options |
|------------|----------------|
| SQL Server | `sqlserver` (Windows), `sspi`, `ServicePrincipal` |
| Databricks | `PersonalAccessToken`, `OAuth`, `auth-pass` (PAT via prompt) |
| Snowflake | `snowflake_auth`, `externalbrowser` |
| BigQuery | Service account, OAuth |

---

## Extract vs Live

Extracts add an `<extract>` with a Hyper (or other) connection:

```xml
<datasource ... >
  <connection ... />
  <extract count='-1' enabled='true' units='records'>
    <connection class='hyper' ... />
  </extract>
</datasource>
```

`count='-1'` means all rows; otherwise set a row limit.

---

## Mixed Workbook Pattern

Combine `sqlproxy` and `federated` in one `<datasources>` block:

```xml
<datasources>
  <datasource hasconnection='false' inline='true' name='Parameters' version='18.1'>...</datasource>

  <datasource caption='Revenue view (Databricks)' inline='true'
              name='sqlproxy.1rjoce80lznlr51d1a5wz11b4hq1' version='18.1'>
    <repository-location ... site='your-site-name' />
    <connection class='sqlproxy' dbname='YourRevenueView' server='your-pod.online.tableau.com' ...>
      <relation type='collection'>
        <relation connection='sqlproxy.1rjoce80lznlr51d1a5wz11b4hq1' name='sqlproxy' table='[sqlproxy]' type='table' />
      </relation>
    </connection>
  </datasource>

  <datasource caption='new_paid_users_ytd(prep)' inline='true'
              name='federated.02bm58x14zgdy9188vvi70n3vz3a' version='18.1'>
    <connection class='federated'>
      <named-connections>...</named-connections>
      <relation name='Custom SQL Query' type='text'>...</relation>
    </connection>
  </datasource>
</datasources>
```

Worksheet fields reference datasource by `name`:

- `[sqlproxy.1rjoce80lznlr51d1a5wz11b4hq1].[sum:Sales:qk]`
- `[federated.02bm58x14zgdy9188vvi70n3vz3a].[max:cumulative_current_year:qk]`

---

## Python Generation Template

Canonical patterns for emitting connection XML. Adjust element trees to match your workbook builder.

### 1) Direct (federated) Databricks datasource

```python
import xml.etree.ElementTree as ET
import secrets

def generate_direct_databricks_datasource(
    caption: str,
    server: str,
    catalog: str,
    schema: str,
    warehouse_http_path: str,
    sql_query: str | None = None,
    table_name: str | None = None,
    columns: list[dict] | None = None,
) -> tuple[ET.Element, str, str]:
    ds_id = f"federated.{secrets.token_hex(12)}"
    conn_id = f"databricks.{secrets.token_hex(12)}"

    ds = ET.Element("datasource")
    ds.set("caption", caption)
    ds.set("inline", "true")
    ds.set("name", ds_id)
    ds.set("version", "18.1")

    conn = ET.SubElement(ds, "connection")
    conn.set("class", "federated")

    named_conns = ET.SubElement(conn, "named-connections")
    named_conn = ET.SubElement(named_conns, "named-connection")
    named_conn.set("caption", server)
    named_conn.set("name", conn_id)

    db_conn = ET.SubElement(named_conn, "connection")
    db_conn.set("authentication", "auth-pass")
    db_conn.set("authentication-type", "")
    db_conn.set("class", "databricks")
    db_conn.set("dbname", catalog)
    db_conn.set("odbc-connect-string-extras", "")
    db_conn.set("one-time-sql", "")
    db_conn.set("schema", schema)
    db_conn.set("server", server)
    db_conn.set("server-oauth", "")
    db_conn.set("username", "")
    db_conn.set("v-http-path", warehouse_http_path)
    db_conn.set("workgroup-auth-mode", "prompt")
    # Omit connection-customization for programmatic generation (programmatic-twb-learnings §2)

    if sql_query:
        relation = ET.SubElement(conn, "relation")
        relation.set("connection", conn_id)
        relation.set("name", "Custom SQL Query")
        relation.set("type", "text")
        relation.text = sql_query
    elif table_name:
        relation = ET.SubElement(conn, "relation")
        relation.set("connection", conn_id)
        relation.set("name", table_name)
        relation.set("table", f"[{catalog}].[{schema}].[{table_name}]")
        relation.set("type", "table")

    if columns:
        type_map = {
            "integer": ("3", "Sum", "10", "SQL_INTEGER", "SQL_C_SLONG"),
            "real": ("5", "Sum", "4", "SQL_DOUBLE", "SQL_C_DOUBLE"),
            "date": ("7", "Year", None, "SQL_TYPE_DATE", "SQL_C_TYPE_DATE"),
            "datetime": ("7", "Year", None, "SQL_TYPE_TIMESTAMP", "SQL_C_TYPE_TIMESTAMP"),
            "string": ("12", "Count", None, "SQL_VARCHAR", "SQL_C_CHAR"),
            "boolean": ("11", "Count", None, "SQL_BIT", "SQL_C_BIT"),
        }
        parent = "[Custom SQL Query]" if sql_query else f"[{table_name}]"

        md = ET.SubElement(conn, "metadata-records")
        for i, col in enumerate(columns, 1):
            lt = col.get("local_type", "string")
            rt, agg, prec, debug_remote, debug_wire = type_map.get(lt, type_map["string"])

            rec = ET.SubElement(md, "metadata-record")
            rec.set("class", "column")
            ET.SubElement(rec, "remote-name").text = col["name"]
            ET.SubElement(rec, "remote-type").text = rt
            ET.SubElement(rec, "local-name").text = f"[{col['name']}]"
            ET.SubElement(rec, "parent-name").text = parent
            ET.SubElement(rec, "remote-alias").text = col["name"]
            ET.SubElement(rec, "ordinal").text = str(col.get("ordinal", i))
            ET.SubElement(rec, "local-type").text = lt
            ET.SubElement(rec, "aggregation").text = col.get("aggregation", agg)
            if prec:
                ET.SubElement(rec, "precision").text = prec
            ET.SubElement(rec, "contains-null").text = str(col.get("nullable", True)).lower()

            attrs = ET.SubElement(rec, "attributes")
            a1 = ET.SubElement(attrs, "attribute")
            a1.set("datatype", "string")
            a1.set("name", "DebugRemoteType")
            a1.text = f'"{debug_remote}"'
            a2 = ET.SubElement(attrs, "attribute")
            a2.set("datatype", "string")
            a2.set("name", "DebugWireType")
            a2.text = f'"{debug_wire}"'

    ET.SubElement(ds, "aliases").set("enabled", "yes")
    return ds, ds_id, conn_id
```

**Usage**

```python
ds_element, ds_id, conn_id = generate_direct_databricks_datasource(
    caption="Users >= 1000$",
    server="dbc-XXXX.cloud.databricks.com",
    catalog="your-catalog",
    schema="marts",
    warehouse_http_path="/sql/1.0/warehouses/WAREHOUSE_ID",
    sql_query="""
        SELECT user_id, paid_date, SUM(usd_net_total) AS net_collection
        FROM `your-catalog`.marts.order_items_status
        WHERE order_status = 'COMPLETED'
        GROUP BY user_id, paid_date
    """,
    columns=[
        {"name": "user_id", "local_type": "integer"},
        {"name": "paid_date", "local_type": "date"},
        {"name": "net_collection", "local_type": "real"},
    ],
)
```

Use **real** server and warehouse values from **[databricks-connection-config.md](databricks-connection-config.md)** where applicable.

### 2) Published `sqlproxy` datasource (workbook fragment)

```python
import xml.etree.ElementTree as ET
import secrets

def add_published_datasource(
    datasources_parent: ET.Element,
    datasource_name: str,
    server_url: str,
    site_name: str,
    columns: list[dict],
) -> str:
    ds_ref = f"sqlproxy.{secrets.token_hex(10)}"
    ds = ET.SubElement(datasources_parent, "datasource")
    ds.set("caption", f"{datasource_name} (Published)")
    ds.set("inline", "true")
    ds.set("name", ds_ref)
    ds.set("version", "18.1")

    repo_loc = ET.SubElement(ds, "repository-location")
    repo_loc.set(
        "derived-from",
        f"http://{server_url}/t/{site_name}/datasources/{datasource_name}?rev=1.0",
    )
    repo_loc.set("id", datasource_name)
    repo_loc.set("path", f"/t/{site_name}/datasources")
    repo_loc.set("revision", "1.0")
    repo_loc.set("site", site_name)

    conn = ET.SubElement(ds, "connection")
    conn.set("channel", "https")
    conn.set("class", "sqlproxy")
    conn.set("dbname", datasource_name)
    conn.set("directory", "/dataserver")
    conn.set("local-dataserver", "")
    conn.set("port", "443")
    conn.set("server", server_url)
    conn.set("server-ds-friendly-name", f"{datasource_name} (Published)")
    conn.set("server-oauth", "")
    conn.set("username", "")
    conn.set("workgroup-auth-mode", "prompt")

    rel_coll = ET.SubElement(conn, "relation")
    rel_coll.set("type", "collection")
    rel = ET.SubElement(rel_coll, "relation")
    rel.set("connection", ds_ref)
    rel.set("name", "sqlproxy")
    rel.set("table", "[sqlproxy]")
    rel.set("type", "table")

    for col in columns:
        c = ET.SubElement(ds, "column")
        c.set("datatype", col["datatype"])
        c.set("name", f"[{col['name']}]")
        c.set("role", col.get("role", "dimension"))
        c.set("type", col.get("type", "nominal"))

    return ds_ref
```

---

## Production Patterns

From KPI-tracking and management-style workbooks:

- **Datasource IDs**: Use opaque ids — `sqlproxy.<long hex>` and `federated.<long hex>` — not display names.
- **Paths**: Prefer `path='/t/{site}/datasources'` and a meaningful `derived-from` URL for traceability.
- **Relations**: `type='collection'` with `connection` on inner `relation` matching the datasource `name` when required.
- **Calculations on published DS**: Keep ROI/CAC-style calcs in `<calculations>` with proper XML escaping.
- **MCP**: Use Tableau MCP to list datasources, fetch metadata (columns, types), and search — reduces manual errors when filling `repository-location` and column lists.
- **REST**: `tableauserverclient` for LUID, project, and publish with `skip_connection_check=True` for sqlproxy.
- **Workbook `repository-location`**: Published workbooks may include a top-level `repository-location` for the `.twb` itself (revision tracking).

**Best practices**

1. Use full datasource path format under `/t/{site}/datasources` when matching production behavior.
2. Keep `id`, `dbname`, and connection `dbname` aligned.
3. Include optional connection attributes (`server-ds-friendly-name`, `saved-credentials-viewerid`) when mirroring Desktop compatibility.
4. For programmatic generation, follow **[programmatic-twb-learnings.md](programmatic-twb-learnings.md)** §1–§2 (child order, `aliases` before `column`, `metadata-records` for Custom SQL, omit `connection-customization`).

---

## Connection Customization (TDC) — reference

Embedded customization (often Postgres/ODBC examples):

```xml
<connection-customization class='postgres' enabled='true' version='18.1'>
  <vendor name='postgres' />
  <driver name='postgres' />
  <customizations>
    <customization name='CAP_FAST_METADATA' value='yes' />
    <customization name='CAP_QUERY_TOP_N' value='yes' />
  </customizations>
</connection-customization>
```

Common capability names include `CAP_FAST_METADATA`, `CAP_QUERY_TOP_N`, `CAP_TEMP_TABLES`, `CAP_JDBC_QUERY_CANCEL`. For **Databricks** programmatic TWBs, prefer omitting this block; see **Databricks Connection Attributes**.
