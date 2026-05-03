# Tableau REST API Reference

The Tableau Server REST API enables programmatic management of Tableau Server and Tableau Cloud resources. This complements TWB XML manipulation by allowing you to publish, download, and manage workbooks on the server.

## API Overview

**Base URLs:**
- Tableau Server: `https://{server}/api/{api-version}/`
- Tableau Cloud: `https://{pod}.online.tableau.com/api/{api-version}/`

**Current API Version:** 3.28 (Tableau Server 26.1)

**Schema XSD:** https://help.tableau.com/samples/en-us/rest_api/ts-api_3_28.xsd

## Authentication

### Sign In Request
```xml
POST /api/3.28/auth/signin

<tsRequest>
  <credentials name="username" password="password">
    <site contentUrl="site-name"/>  <!-- Empty for default site -->
  </credentials>
</tsRequest>
```

### Sign In Response
```xml
<tsResponse>
  <credentials token="authentication-token">
    <site id="site-id" contentUrl="site-name"/>
    <user id="user-id"/>
  </credentials>
</tsResponse>
```

### Using Personal Access Token (PAT)
```xml
<tsRequest>
  <credentials personalAccessTokenName="token-name" 
               personalAccessTokenSecret="token-secret">
    <site contentUrl="site-name"/>
  </credentials>
</tsRequest>
```

### Request Headers (After Sign In)
```
X-Tableau-Auth: {authentication-token}
Content-Type: text/xml  (or application/json)
Accept: application/xml (or application/json)
```

## Publishing Workbooks

### Single Request (< 64MB)
```
POST /api/3.28/sites/{site-id}/workbooks?overwrite=true
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Disposition: name="request_payload"
Content-Type: text/xml

<tsRequest>
  <workbook name="workbook-name" showTabs="true">
    <project id="project-id"/>
    <connectionCredentials name="db-user" password="db-password" embed="true"/>
  </workbook>
</tsRequest>
--{boundary}
Content-Disposition: name="tableau_workbook"; filename="workbook.twbx"
Content-Type: application/octet-stream

{binary workbook content}
--{boundary}--
```

### Multi-Part Upload (> 64MB)

**Step 1: Initiate Upload**
```
POST /api/3.28/sites/{site-id}/fileUploads
```

Response:
```xml
<tsResponse>
  <fileUpload uploadSessionId="upload-session-id" fileSize="0"/>
</tsResponse>
```

**Step 2: Append Chunks (5MB each)**
```
PUT /api/3.28/sites/{site-id}/fileUploads/{upload-session-id}
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Disposition: name="request_payload"
Content-Type: text/xml

--{boundary}
Content-Disposition: name="tableau_file"; filename="chunk"
Content-Type: application/octet-stream

{binary chunk data}
--{boundary}--
```

**Step 3: Commit Upload**
```
POST /api/3.28/sites/{site-id}/workbooks?uploadSessionId={upload-session-id}&workbookType=twbx

<tsRequest>
  <workbook name="workbook-name" showTabs="true">
    <project id="project-id"/>
  </workbook>
</tsRequest>
```

### Publish Response
```xml
<tsResponse>
  <workbook id="workbook-id" name="workbook-name" contentUrl="workbook-url" 
            createdAt="2025-01-24T10:30:00Z" updatedAt="2025-01-24T10:30:00Z">
    <project id="project-id" name="project-name"/>
    <owner id="user-id"/>
    <views>
      <view id="view-id" name="Sheet1" contentUrl="workbook-url/sheets/Sheet1"/>
    </views>
  </workbook>
</tsResponse>
```

## Downloading Workbooks

### Download Workbook
```
GET /api/3.28/sites/{site-id}/workbooks/{workbook-id}/content?includeExtract=false
```
Response: Binary .twb or .twbx file

### Query Workbook Info
```
GET /api/3.28/sites/{site-id}/workbooks/{workbook-id}
```

Response:
```xml
<tsResponse>
  <workbook id="workbook-id" name="workbook-name" contentUrl="url"
            createdAt="..." updatedAt="..." encryptExtracts="false">
    <project id="..." name="..."/>
    <owner id="..." name="..."/>
    <tags>
      <tag label="sales"/>
    </tags>
    <views>
      <view id="..." name="Sheet 1" contentUrl="..."/>
    </views>
  </workbook>
</tsResponse>
```

## Data Sources

### Publish Data Source
```
POST /api/3.28/sites/{site-id}/datasources?overwrite=true
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Disposition: name="request_payload"
Content-Type: text/xml

<tsRequest>
  <datasource name="datasource-name" description="description">
    <project id="project-id"/>
    <connectionCredentials name="user" password="pass" embed="true"/>
  </datasource>
</tsRequest>
--{boundary}
Content-Disposition: name="tableau_datasource"; filename="datasource.tdsx"
Content-Type: application/octet-stream

{binary content}
--{boundary}--
```

### Query Data Sources
```
GET /api/3.28/sites/{site-id}/datasources
```

### Update Data Source Connection
```
PUT /api/3.28/sites/{site-id}/datasources/{datasource-id}/connections/{connection-id}

<tsRequest>
  <connection serverAddress="new-server" serverPort="5432"
              userName="new-user" password="new-password" embedPassword="true"/>
</tsRequest>
```

## Projects

### Create Project
```
POST /api/3.28/sites/{site-id}/projects

<tsRequest>
  <project name="New Project" description="Project description"
           contentPermissions="ManagedByOwner"/>
</tsRequest>
```

### Query Projects
```
GET /api/3.28/sites/{site-id}/projects
```

Response:
```xml
<tsResponse>
  <pagination pageNumber="1" pageSize="100" totalAvailable="5"/>
  <projects>
    <project id="project-id" name="Default" description="..."
             contentPermissions="ManagedByOwner" createdAt="..." updatedAt="..."/>
  </projects>
</tsResponse>
```

## Users and Groups

### Add User to Site
```
POST /api/3.28/sites/{site-id}/users

<tsRequest>
  <user name="user@example.com" siteRole="Creator" authSetting="SAML"/>
</tsRequest>
```

**Site Roles:** Creator, Explorer, ExplorerCanPublish, Guest, ServerAdministrator, SiteAdministratorCreator, SiteAdministratorExplorer, SupportUser, Unlicensed, Viewer

### Query Users
```
GET /api/3.28/sites/{site-id}/users?filter=siteRole:eq:Creator
```

### Create Group
```
POST /api/3.28/sites/{site-id}/groups

<tsRequest>
  <group name="Marketing Team"/>
</tsRequest>
```

## Permissions

### Add Workbook Permissions
```
PUT /api/3.28/sites/{site-id}/workbooks/{workbook-id}/permissions

<tsRequest>
  <permissions>
    <workbook id="workbook-id"/>
    <granteeCapabilities>
      <user id="user-id"/>
      <capabilities>
        <capability name="Read" mode="Allow"/>
        <capability name="Write" mode="Allow"/>
        <capability name="ExportData" mode="Deny"/>
      </capabilities>
    </granteeCapabilities>
    <granteeCapabilities>
      <group id="group-id"/>
      <capabilities>
        <capability name="Read" mode="Allow"/>
      </capabilities>
    </granteeCapabilities>
  </permissions>
</tsRequest>
```

**Capability Names:** AddComment, ChangeHierarchy, ChangePermissions, Delete, ExportData, ExportImage, ExportXml, Filter, Read, ShareView, ViewComments, ViewUnderlyingData, WebAuthoring, Write

**Modes:** Allow, Deny

**Permissions on Group Sets:** In 3.28, `granteeCapabilities` can also reference a `groupSet` (in addition to `user` and `group`).

## Extract Refresh

### Run Extract Refresh Now
```
POST /api/3.28/sites/{site-id}/workbooks/{workbook-id}/refresh
```

### Create Cloud Extract Refresh Task
```
POST /api/3.28/sites/{site-id}/tasks/extractRefreshes

<tsRequest>
  <extractRefresh>
    <workbook id="workbook-id"/>
    <schedule frequency="Daily" startTime="02:00:00">
      <frequencyDetails start="02:00:00">
        <intervals>
          <interval hours="24"/>
        </intervals>
      </frequencyDetails>
    </schedule>
  </extractRefresh>
</tsRequest>
```

## Views

### Query View Image
```
GET /api/3.28/sites/{site-id}/views/{view-id}/image?resolution=high
```
Response: PNG image

### Query View PDF
```
GET /api/3.28/sites/{site-id}/views/{view-id}/pdf?type=A4&orientation=Landscape
```

### Query View Data (CSV)
```
GET /api/3.28/sites/{site-id}/views/{view-id}/data?maxAge=60
```

### Filter View Data
```
GET /api/3.28/sites/{site-id}/views/{view-id}/data?vf_Region=West&vf_Category=Technology
```

## Subscriptions

### Create Subscription
```
POST /api/3.28/sites/{site-id}/subscriptions

<tsRequest>
  <subscription subject="Weekly Sales Report">
    <content id="workbook-id" type="Workbook"/>
    <schedule id="schedule-id"/>
    <user id="user-id"/>
  </subscription>
</tsRequest>
```

## Webhooks

### Create Webhook
```
POST /api/3.28/sites/{site-id}/webhooks

<tsRequest>
  <webhook name="workbook-refresh-webhook">
    <webhook-source>
      <webhook-source-event-datasource-refresh-succeeded/>
    </webhook-source>
    <webhook-destination>
      <webhook-destination-http method="POST" url="https://example.com/webhook"/>
    </webhook-destination>
  </webhook>
</tsRequest>
```

**Webhook Events:**
- datasource-refresh-started/succeeded/failed
- datasource-created/updated/deleted
- workbook-refresh-started/succeeded/failed
- workbook-created/updated/deleted
- view-deleted
- label-created/updated/deleted
- flow-completed

## Jobs

### Query Job Status
```
GET /api/3.28/sites/{site-id}/jobs/{job-id}
```

Response:
```xml
<tsResponse>
  <job id="job-id" mode="Asynchronous" type="RefreshExtract" 
       progress="50" createdAt="..." startedAt="..." completedAt="...">
    <statusNotes>
      <statusNote type="statusNote" value="Running..."/>
    </statusNotes>
  </job>
</tsResponse>
```

### Cancel Job
```
PUT /api/3.28/sites/{site-id}/jobs/{job-id}

<tsRequest>
  <job canceled="true"/>
</tsRequest>
```

## Common Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `pageSize` | Results per page (max 1000) | `?pageSize=100` |
| `pageNumber` | Page number | `?pageNumber=2` |
| `filter` | Filter results | `?filter=name:eq:Sales` |
| `sort` | Sort results | `?sort=name:asc` |
| `fields` | Limit returned fields | `?fields=id,name,owner` |

### Filter Operators
- `eq` - equals
- `in` - in list (comma-separated)
- `gt`, `gte` - greater than (or equal)
- `lt`, `lte` - less than (or equal)
- `has` - contains substring

## Error Handling

```xml
<tsResponse>
  <error code="401002">
    <summary>Signin Error</summary>
    <detail>Invalid credentials</detail>
  </error>
</tsResponse>
```

Common Error Codes:
- 400xxx - Bad Request
- 401xxx - Authentication errors  
- 403xxx - Permission errors
- 404xxx - Not found
- 409xxx - Conflict
- 429xxx - Rate limit exceeded

## Python Example with tableauserverclient

```python
import tableauserverclient as TSC

# Connect
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name='my-token',
    personal_access_token='secret',
    site_id='my-site'
)
server = TSC.Server('https://10ax.online.tableau.com', use_server_version=True)

with server.auth.sign_in(tableau_auth):
    # Get all workbooks
    all_workbooks, pagination = server.workbooks.get()
    
    # Download workbook
    workbook = server.workbooks.get_by_id('workbook-id')
    server.workbooks.download('workbook-id', filepath='/tmp/workbook.twbx')
    
    # Publish workbook
    new_workbook = TSC.WorkbookItem(project_id='project-id', name='My Workbook')
    new_workbook = server.workbooks.publish(
        new_workbook, 
        '/path/to/workbook.twbx',
        mode=TSC.Server.PublishMode.Overwrite
    )
    
    # Refresh extract
    server.workbooks.refresh(new_workbook.id)
```

## cURL Examples

### Sign In
```bash
curl -X POST "https://server/api/3.28/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"credentials":{"name":"user","password":"pass","site":{"contentUrl":""}}}'
```

### Publish Workbook
```bash
curl -X POST "https://server/api/3.28/sites/{site-id}/workbooks?overwrite=true" \
  -H "X-Tableau-Auth: {token}" \
  -H "Content-Type: multipart/mixed; boundary=boundary123" \
  -F "request_payload=@publish.xml" \
  -F "tableau_workbook=@workbook.twbx"
```

### Download Workbook
```bash
curl -X GET "https://server/api/3.28/sites/{site-id}/workbooks/{workbook-id}/content" \
  -H "X-Tableau-Auth: {token}" \
  -o workbook.twbx
```

## New in API 3.28 (Tableau Server 26.1)

### Key Changes from 3.27

| Feature | Description |
|---------|-------------|
| **Generative AI** | `generativeAiRegistration` / `generativeAiCheckRegistration` types for AI registration management; many new site-level GenAI settings (Pulse, Data Catalog, Web Authoring, Prep) |
| **Collections** | `collectionType` for organizing content into curated collections (owner, visibility, item counts) |
| **Lenses (Pulse)** | `lensType` for Tableau Pulse metric definitions |
| **Group Sets** | `groupSetType` / `groupSetListType` for managing sets of groups; group sets can be used in permissions (`granteeCapabilities`) |
| **Flow Parameters** | Extensive new types for parameterized flows (`flowParameterType`, domain types: any, binary, list, range, system) |
| **Personal Space** | `personalSpaceType` for user personal spaces |
| **Bridge/Edge Pools** | Enhanced bridge client management (`bridgeClientMoveRequestType`), edge pool domains |
| **Data Alerts** | Enhanced with `dataAlertsRecipientType` and `dataAlertUpdateStatusType` for managing alert recipients and status updates |
| **Webhook Events** | New events: `label-created/deleted/updated`, `view-deleted` |
| **Site Settings** | New attributes: `recycleBinEnabled`, `cmekEnabled`, `pulseEnabled`, `pulsePersonalizedRankingEnabled`, `generativeAiPulseDiscoverEnabled`, `generativeAiWebAuthoringOnPremEnabled`, `groupSetsEnabled`, `sitePromptedLoginFlowEnabled`, many more |
| **Site Roles** | `Guest`, `ServerAdministrator`, `SupportUser` added to `siteRoleType` |
| **Data Source** | New `hasSemanticLayerConnection` attribute |
| **User** | New attributes: `glsiMinimumSiteRole`, `identityPoolName`, `identityPoolUuid`, `identityUuid`, `idpConfigurationId/Name` |
| **Connected Apps** | Project-scoping via `connectedApplicationProjectListType` |
| **OIDC** | `siteOIDCConfiguration` / `siteAuthConfigurations` for site-level auth config management |

### Collections API

```
POST /api/3.28/sites/{site-id}/collections
GET  /api/3.28/sites/{site-id}/collections
```

### Generative AI Registration

```
GET /api/3.28/sites/{site-id}/generativeAiCheckRegistration
```

Response includes `domain`, `orgid`, `registered`, `username`.

### Pulse / Lenses

Lenses represent Tableau Pulse metric definitions:
```xml
<tsResponse>
  <lens id="lens-id" name="Revenue Metric">
    <owner id="user-id"/>
  </lens>
</tsResponse>
```

## Resources

- **Official Documentation:** https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
- **API Reference:** https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm
- **XSD Schemas:** https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_schema.htm
- **Python Client:** https://tableau.github.io/server-client-python/
- **Sample Code:** https://github.com/tableau/rest-api-samples
