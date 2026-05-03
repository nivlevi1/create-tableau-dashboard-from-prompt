#!/usr/bin/env python3
"""
Tableau REST API Client

A simple client for interacting with Tableau Server/Cloud REST API.
For production use, consider the official tableauserverclient library:
pip install tableauserverclient

Usage:
    client = TableauRestClient('https://server.com', api_version='3.28')
    client.sign_in('username', 'password', 'site-name')
    
    # List projects
    projects = client.get_projects()
    
    # Publish workbook
    client.publish_workbook('/path/to/workbook.twbx', 'project-id', 'Workbook Name')
    
    # Download workbook
    client.download_workbook('workbook-id', '/path/to/download.twbx')
    
    client.sign_out()
"""

import requests
import xml.etree.ElementTree as ET
import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Union

# API namespace for parsing responses
XMLNS = {'t': 'http://tableau.com/api'}

class TableauRestClient:
    """Simple Tableau REST API client."""
    
    def __init__(self, server_url: str, api_version: str = '3.28'):
        """
        Initialize client.
        
        Args:
            server_url: Tableau Server/Cloud URL (e.g., 'https://10ax.online.tableau.com')
            api_version: REST API version (default: 3.28)
        """
        self.server_url = server_url.rstrip('/')
        self.api_version = api_version
        self.base_url = f"{self.server_url}/api/{api_version}"
        self.auth_token: Optional[str] = None
        self.site_id: Optional[str] = None
        self.user_id: Optional[str] = None
    
    def _headers(self, content_type: str = 'application/xml') -> Dict[str, str]:
        """Get request headers."""
        headers = {'Content-Type': content_type, 'Accept': 'application/xml'}
        if self.auth_token:
            headers['X-Tableau-Auth'] = self.auth_token
        return headers
    
    def _check_response(self, response: requests.Response, expected_status: int = 200) -> None:
        """Check response for errors."""
        if response.status_code != expected_status:
            try:
                root = ET.fromstring(response.content)
                error = root.find('.//t:error', XMLNS)
                if error is not None:
                    code = error.get('code', 'unknown')
                    summary = error.findtext('t:summary', 'Unknown error', XMLNS)
                    detail = error.findtext('t:detail', '', XMLNS)
                    raise Exception(f"Tableau API Error {code}: {summary} - {detail}")
            except ET.ParseError:
                pass
            raise Exception(f"HTTP {response.status_code}: {response.text[:500]}")
    
    def sign_in(self, username: str, password: str, site_content_url: str = '') -> Dict[str, str]:
        """
        Sign in to Tableau Server/Cloud.
        
        Args:
            username: Tableau username
            password: Tableau password
            site_content_url: Site name (empty string for default site)
        
        Returns:
            Dict with token, site_id, user_id
        """
        url = f"{self.base_url}/auth/signin"
        
        # Build request XML
        request = ET.Element('tsRequest')
        credentials = ET.SubElement(request, 'credentials', name=username, password=password)
        ET.SubElement(credentials, 'site', contentUrl=site_content_url)
        
        body = ET.tostring(request, encoding='unicode')
        response = requests.post(url, data=body, headers=self._headers())
        self._check_response(response)
        
        # Parse response
        root = ET.fromstring(response.content)
        creds = root.find('.//t:credentials', XMLNS)
        site = creds.find('t:site', XMLNS)
        user = creds.find('t:user', XMLNS)
        
        self.auth_token = creds.get('token')
        self.site_id = site.get('id')
        self.user_id = user.get('id')
        
        return {
            'token': self.auth_token,
            'site_id': self.site_id,
            'user_id': self.user_id
        }
    
    def sign_in_with_pat(self, token_name: str, token_secret: str, 
                         site_content_url: str = '') -> Dict[str, str]:
        """
        Sign in using Personal Access Token.
        
        Args:
            token_name: PAT name
            token_secret: PAT secret
            site_content_url: Site name
        
        Returns:
            Dict with token, site_id, user_id
        """
        url = f"{self.base_url}/auth/signin"
        
        request = ET.Element('tsRequest')
        credentials = ET.SubElement(request, 'credentials',
                                   personalAccessTokenName=token_name,
                                   personalAccessTokenSecret=token_secret)
        ET.SubElement(credentials, 'site', contentUrl=site_content_url)
        
        body = ET.tostring(request, encoding='unicode')
        response = requests.post(url, data=body, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        creds = root.find('.//t:credentials', XMLNS)
        site = creds.find('t:site', XMLNS)
        user = creds.find('t:user', XMLNS)
        
        self.auth_token = creds.get('token')
        self.site_id = site.get('id')
        self.user_id = user.get('id')
        
        return {
            'token': self.auth_token,
            'site_id': self.site_id,
            'user_id': self.user_id
        }
    
    def sign_out(self) -> None:
        """Sign out and invalidate token."""
        if self.auth_token:
            url = f"{self.base_url}/auth/signout"
            requests.post(url, headers=self._headers())
            self.auth_token = None
            self.site_id = None
            self.user_id = None
    
    def get_projects(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get all projects in the site.
        
        Returns:
            List of project dicts with id, name, description, etc.
        """
        url = f"{self.base_url}/sites/{self.site_id}/projects?pageSize={page_size}"
        response = requests.get(url, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        projects = []
        for proj in root.findall('.//t:project', XMLNS):
            projects.append({
                'id': proj.get('id'),
                'name': proj.get('name'),
                'description': proj.get('description', ''),
                'content_permissions': proj.get('contentPermissions'),
                'parent_project_id': proj.get('parentProjectId')
            })
        return projects
    
    def create_project(self, name: str, description: str = '', 
                       parent_project_id: Optional[str] = None) -> Dict[str, str]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            parent_project_id: Parent project ID for nested projects
        
        Returns:
            Dict with id, name
        """
        url = f"{self.base_url}/sites/{self.site_id}/projects"
        
        request = ET.Element('tsRequest')
        project_attrs = {'name': name, 'description': description}
        if parent_project_id:
            project_attrs['parentProjectId'] = parent_project_id
        ET.SubElement(request, 'project', **project_attrs)
        
        body = ET.tostring(request, encoding='unicode')
        response = requests.post(url, data=body, headers=self._headers())
        self._check_response(response, 201)
        
        root = ET.fromstring(response.content)
        proj = root.find('.//t:project', XMLNS)
        return {'id': proj.get('id'), 'name': proj.get('name')}
    
    def get_workbooks(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get all workbooks in the site.
        
        Returns:
            List of workbook dicts
        """
        url = f"{self.base_url}/sites/{self.site_id}/workbooks?pageSize={page_size}"
        response = requests.get(url, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        workbooks = []
        for wb in root.findall('.//t:workbook', XMLNS):
            project = wb.find('t:project', XMLNS)
            owner = wb.find('t:owner', XMLNS)
            workbooks.append({
                'id': wb.get('id'),
                'name': wb.get('name'),
                'content_url': wb.get('contentUrl'),
                'created_at': wb.get('createdAt'),
                'updated_at': wb.get('updatedAt'),
                'project_id': project.get('id') if project is not None else None,
                'project_name': project.get('name') if project is not None else None,
                'owner_id': owner.get('id') if owner is not None else None
            })
        return workbooks
    
    def get_workbook(self, workbook_id: str) -> Dict[str, Any]:
        """Get workbook details by ID."""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}"
        response = requests.get(url, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        wb = root.find('.//t:workbook', XMLNS)
        project = wb.find('t:project', XMLNS)
        owner = wb.find('t:owner', XMLNS)
        
        views = []
        for view in wb.findall('.//t:view', XMLNS):
            views.append({
                'id': view.get('id'),
                'name': view.get('name'),
                'content_url': view.get('contentUrl')
            })
        
        return {
            'id': wb.get('id'),
            'name': wb.get('name'),
            'content_url': wb.get('contentUrl'),
            'created_at': wb.get('createdAt'),
            'updated_at': wb.get('updatedAt'),
            'project_id': project.get('id') if project is not None else None,
            'project_name': project.get('name') if project is not None else None,
            'owner_id': owner.get('id') if owner is not None else None,
            'views': views
        }
    
    def download_workbook(self, workbook_id: str, filepath: str, 
                          include_extract: bool = False) -> str:
        """
        Download workbook to file.
        
        Args:
            workbook_id: Workbook ID
            filepath: Local path to save .twbx file
            include_extract: Include extract data in download
        
        Returns:
            Filepath of downloaded workbook
        """
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}/content"
        if not include_extract:
            url += "?includeExtract=false"
        
        response = requests.get(url, headers=self._headers(), stream=True)
        self._check_response(response)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath
    
    def publish_workbook(self, filepath: str, project_id: str, name: str,
                         overwrite: bool = True, show_tabs: bool = True,
                         connection_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Publish workbook to Tableau Server/Cloud.
        
        Args:
            filepath: Path to .twb or .twbx file
            project_id: Target project ID
            name: Workbook name
            overwrite: Overwrite existing workbook
            show_tabs: Show sheet tabs
            connection_credentials: Dict with 'name' and 'password' for embedded connections
        
        Returns:
            Dict with workbook id, name, content_url
        """
        file_size = os.path.getsize(filepath)
        file_ext = Path(filepath).suffix.lower()
        workbook_type = 'twbx' if file_ext == '.twbx' else 'twb'
        
        # Build request XML
        request = ET.Element('tsRequest')
        workbook = ET.SubElement(request, 'workbook', name=name, 
                                showTabs=str(show_tabs).lower())
        ET.SubElement(workbook, 'project', id=project_id)
        
        if connection_credentials:
            conn_creds = ET.SubElement(workbook, 'connectionCredentials',
                                       name=connection_credentials['name'],
                                       password=connection_credentials['password'],
                                       embed='true')
        
        request_xml = ET.tostring(request, encoding='unicode')
        
        # Single request for files < 64MB
        if file_size < 64 * 1024 * 1024:
            return self._publish_single_request(filepath, project_id, name, 
                                                workbook_type, request_xml, overwrite)
        else:
            return self._publish_multipart(filepath, project_id, name,
                                          workbook_type, request_xml, overwrite)
    
    def _publish_single_request(self, filepath: str, project_id: str, name: str,
                                 workbook_type: str, request_xml: str,
                                 overwrite: bool) -> Dict[str, Any]:
        """Publish workbook in single request (< 64MB)."""
        url = f"{self.base_url}/sites/{self.site_id}/workbooks"
        url += f"?workbookType={workbook_type}"
        if overwrite:
            url += "&overwrite=true"
        
        boundary = '----TableauBoundary7MA4YWxkTrZu0gW'
        
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: name="request_payload"\r\n'
            f'Content-Type: text/xml\r\n\r\n'
            f'{request_xml}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: name="tableau_workbook"; filename="{Path(filepath).name}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n'
        ).encode('utf-8') + file_content + f'\r\n--{boundary}--'.encode('utf-8')
        
        headers = self._headers(f'multipart/mixed; boundary={boundary}')
        response = requests.post(url, data=body, headers=headers)
        self._check_response(response, 201)
        
        root = ET.fromstring(response.content)
        wb = root.find('.//t:workbook', XMLNS)
        return {
            'id': wb.get('id'),
            'name': wb.get('name'),
            'content_url': wb.get('contentUrl')
        }
    
    def _publish_multipart(self, filepath: str, project_id: str, name: str,
                           workbook_type: str, request_xml: str,
                           overwrite: bool) -> Dict[str, Any]:
        """Publish workbook in multiple chunks (> 64MB)."""
        # Step 1: Initiate upload
        url = f"{self.base_url}/sites/{self.site_id}/fileUploads"
        response = requests.post(url, headers=self._headers())
        self._check_response(response, 201)
        
        root = ET.fromstring(response.content)
        upload = root.find('.//t:fileUpload', XMLNS)
        upload_session_id = upload.get('uploadSessionId')
        
        # Step 2: Upload chunks
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        boundary = '----TableauBoundary7MA4YWxkTrZu0gW'
        
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                body = (
                    f'--{boundary}\r\n'
                    f'Content-Disposition: name="request_payload"\r\n'
                    f'Content-Type: text/xml\r\n\r\n'
                    f'\r\n'
                    f'--{boundary}\r\n'
                    f'Content-Disposition: name="tableau_file"; filename="chunk"\r\n'
                    f'Content-Type: application/octet-stream\r\n\r\n'
                ).encode('utf-8') + chunk + f'\r\n--{boundary}--'.encode('utf-8')
                
                headers = self._headers(f'multipart/mixed; boundary={boundary}')
                url = f"{self.base_url}/sites/{self.site_id}/fileUploads/{upload_session_id}"
                response = requests.put(url, data=body, headers=headers)
                self._check_response(response)
        
        # Step 3: Commit upload
        url = f"{self.base_url}/sites/{self.site_id}/workbooks"
        url += f"?uploadSessionId={upload_session_id}&workbookType={workbook_type}"
        if overwrite:
            url += "&overwrite=true"
        
        response = requests.post(url, data=request_xml, headers=self._headers())
        self._check_response(response, 201)
        
        root = ET.fromstring(response.content)
        wb = root.find('.//t:workbook', XMLNS)
        return {
            'id': wb.get('id'),
            'name': wb.get('name'),
            'content_url': wb.get('contentUrl')
        }
    
    def refresh_workbook(self, workbook_id: str) -> str:
        """
        Trigger extract refresh for workbook.
        
        Returns:
            Job ID for tracking refresh status
        """
        url = f"{self.base_url}/sites/{self.site_id}/workbooks/{workbook_id}/refresh"
        request = ET.Element('tsRequest')
        body = ET.tostring(request, encoding='unicode')
        
        response = requests.post(url, data=body, headers=self._headers())
        self._check_response(response, 202)
        
        root = ET.fromstring(response.content)
        job = root.find('.//t:job', XMLNS)
        return job.get('id')
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status."""
        url = f"{self.base_url}/sites/{self.site_id}/jobs/{job_id}"
        response = requests.get(url, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        job = root.find('.//t:job', XMLNS)
        return {
            'id': job.get('id'),
            'mode': job.get('mode'),
            'type': job.get('type'),
            'progress': job.get('progress'),
            'created_at': job.get('createdAt'),
            'started_at': job.get('startedAt'),
            'completed_at': job.get('completedAt'),
            'finish_code': job.get('finishCode')
        }
    
    def get_datasources(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get all data sources in the site."""
        url = f"{self.base_url}/sites/{self.site_id}/datasources?pageSize={page_size}"
        response = requests.get(url, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        datasources = []
        for ds in root.findall('.//t:datasource', XMLNS):
            project = ds.find('t:project', XMLNS)
            owner = ds.find('t:owner', XMLNS)
            datasources.append({
                'id': ds.get('id'),
                'name': ds.get('name'),
                'content_url': ds.get('contentUrl'),
                'type': ds.get('type'),
                'created_at': ds.get('createdAt'),
                'updated_at': ds.get('updatedAt'),
                'project_id': project.get('id') if project is not None else None,
                'owner_id': owner.get('id') if owner is not None else None
            })
        return datasources
    
    def get_users(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get all users in the site."""
        url = f"{self.base_url}/sites/{self.site_id}/users?pageSize={page_size}"
        response = requests.get(url, headers=self._headers())
        self._check_response(response)
        
        root = ET.fromstring(response.content)
        users = []
        for user in root.findall('.//t:user', XMLNS):
            users.append({
                'id': user.get('id'),
                'name': user.get('name'),
                'site_role': user.get('siteRole'),
                'last_login': user.get('lastLogin'),
                'external_auth_user_id': user.get('externalAuthUserId')
            })
        return users
    
    def download_view_image(self, view_id: str, filepath: str,
                            resolution: str = 'high') -> str:
        """
        Download view as PNG image.
        
        Args:
            view_id: View ID
            filepath: Path to save PNG
            resolution: 'high' or 'standard'
        
        Returns:
            Filepath of saved image
        """
        url = f"{self.base_url}/sites/{self.site_id}/views/{view_id}/image"
        url += f"?resolution={resolution}"
        
        response = requests.get(url, headers=self._headers(), stream=True)
        self._check_response(response)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath
    
    def download_view_pdf(self, view_id: str, filepath: str,
                          page_type: str = 'A4',
                          orientation: str = 'Portrait') -> str:
        """
        Download view as PDF.
        
        Args:
            view_id: View ID
            filepath: Path to save PDF
            page_type: 'A3', 'A4', 'A5', 'B5', 'Executive', 'Folio', 'Ledger', 
                       'Legal', 'Letter', 'Note', 'Quarto', 'Tabloid'
            orientation: 'Portrait' or 'Landscape'
        
        Returns:
            Filepath of saved PDF
        """
        url = f"{self.base_url}/sites/{self.site_id}/views/{view_id}/pdf"
        url += f"?type={page_type}&orientation={orientation}"
        
        response = requests.get(url, headers=self._headers(), stream=True)
        self._check_response(response)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tableau REST API Client')
    parser.add_argument('--server', required=True, help='Tableau Server URL')
    parser.add_argument('--username', help='Username')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--token-name', help='PAT name')
    parser.add_argument('--token-secret', help='PAT secret')
    parser.add_argument('--site', default='', help='Site content URL')
    parser.add_argument('--action', choices=['list-projects', 'list-workbooks', 
                                             'download', 'publish', 'refresh'],
                       required=True, help='Action to perform')
    parser.add_argument('--workbook-id', help='Workbook ID for download/refresh')
    parser.add_argument('--filepath', help='File path for download/publish')
    parser.add_argument('--project-id', help='Project ID for publish')
    parser.add_argument('--name', help='Workbook name for publish')
    
    args = parser.parse_args()
    
    client = TableauRestClient(args.server)
    
    try:
        # Sign in
        if args.token_name and args.token_secret:
            client.sign_in_with_pat(args.token_name, args.token_secret, args.site)
        elif args.username and args.password:
            client.sign_in(args.username, args.password, args.site)
        else:
            raise ValueError("Provide either username/password or token-name/token-secret")
        
        # Perform action
        if args.action == 'list-projects':
            projects = client.get_projects()
            for p in projects:
                print(f"{p['id']}: {p['name']}")
        
        elif args.action == 'list-workbooks':
            workbooks = client.get_workbooks()
            for wb in workbooks:
                print(f"{wb['id']}: {wb['name']} (project: {wb['project_name']})")
        
        elif args.action == 'download':
            if not args.workbook_id or not args.filepath:
                raise ValueError("--workbook-id and --filepath required for download")
            path = client.download_workbook(args.workbook_id, args.filepath)
            print(f"Downloaded to: {path}")
        
        elif args.action == 'publish':
            if not args.filepath or not args.project_id or not args.name:
                raise ValueError("--filepath, --project-id, and --name required for publish")
            result = client.publish_workbook(args.filepath, args.project_id, args.name)
            print(f"Published: {result['id']} - {result['name']}")
        
        elif args.action == 'refresh':
            if not args.workbook_id:
                raise ValueError("--workbook-id required for refresh")
            job_id = client.refresh_workbook(args.workbook_id)
            print(f"Refresh job started: {job_id}")
    
    finally:
        client.sign_out()


if __name__ == '__main__':
    main()
