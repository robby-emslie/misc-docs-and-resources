"""
    Workato API Python Library
    
"""

import sys, json, requests, time, datetime, csv

## CONSTANTS

API_ENVIRONMENTS = {
    'us': "https://app.workato.com",
    'eu': "https://app.eu.workato.com",
    'jp': "https://app.jp.workato.com",
    'sg': "https://app.sg.workato.com"
}   # if you would prefer to include the `/api/` directory in the target specification for functions rather than
    # implied by the api_root used globally, you can remove this suffix from each of the above

#
# FUNCTIONS
def generate_response_log_message(response):
    if response.status_code in [200, 201]:
        # may want to expand this with analysisn of the response payload
        # to allow passing more information for analysis
        log_message = f"Request received a sucesssful response."
    elif response.status_code in [400, 401, 402, 403, 404, 405]:
        log_message = f"Request returned {response.status_code}: {response.json()['message']}"
    elif response.status_code in [500]:
        log_message = f"Request generated an internal server error: {response.json()['message']}"
    return log_message


#
# EXCEPTION CLASSES 

class InternalOperationError(Exception):
    def __init__(self, message):
        self.message = message

#
# CLASSES

#
# WorkatoResponse
# The standard repsonse object for API requests
class WorkatoResponse:
    def __init__(self, response_code, response_header, response_message, response_data, log_message):
        self.status_code = response_code
        self.header = response_header
        self.message = response_message
        self.data = response_data
        self.log_message = log_message

#
# WorkatoReport
# Can be used to aggregate details about a Workato environment or elements in the environment.
class WorkatoReport:
    def __init__(self, report_name=None, report_data=None, report_fields=None, report_log=[]):
        """
        Create a new WorkatoReport object.
        """
        self.name = report_name if report_name is not None else f"NewReport_{int(time.time())}"
        self.data = list(report_data) if report_data is not None else None
        self.fields = report_fields if report_fields is not None else None
        self.log = report_log
        self.created = datetime.datetime.now()
        self.modified = self.created
    
    def add_data(self, additional_data, redundancy_field=None):
        """
        Add additional data entries to an existing WorkatoReport object.
        """
        for each_element in additional_data:
            if redundancy_field is None:
                self.data.append(each_element)
        # update modified time stamp
        self.modified = datetime.datetime.now()
    
    def export(self, format='csv', outfile=None):
        """
        Export report in `format`. Options include `csv` and `html`.
        Note that fields containing list or dictionary data types will be converted to strings of
        the data. For more advanced formatting, a custom format script should be created.
        """
        try:
            report_file = f"{outfile}.{format}" if outfile is not None else f"{self.name}.{format}"
        except Exception as ex:
            raise InternalOperationError(ex)
        if self.data is None or self.fields is None:
            raise InternalOperationError(f"WorkatoReport.export(): Cannot export a report with missing fields or data.")
        try:
            if format == 'csv':
                report = "\"" + "\",\"".join(self.fields) + "\""
                for each_entry in self.data:
                    report += "\n"
                    for i in range(0, len(self.fields)):
                        #field = self.fields[i]
                        value = str(each_entry[self.fields[i]]).replace("\"", "'")
                        report += f"\"{value}\""
                        if i < len(self.fields) - 1:
                            report += ","
            elif format == 'html':
                raise Exception(f"WorkatoReport.export(): HTML export is not currently supported.")
        except Exception as ex:
            raise InternalOperationError(f"WorkatoReport.export(): Error parsing report to {format}:\n{ex}")
        return report

#
# Workato
# The core of the library, the Workato class represents an API client and all the various actions available
# to the client through Workato's API.
class Workato:
    #
    # Defining the API Client
    def __init__(self, region, api_token):
        """
        The Workato class represents a useable objecat can be used to make requests from Workato's API. It is
        configured with the Workato region, which is used to establish the root URL for requests to be sent to, and
        an api_token, which is generated for the API client when it is created in Workato. The resulting object has
        the properties `.region` (representing the Workato region), `.api_root` (representing the base URL for the
        connection and all subsequent requests), and `.api_header` (contains the authorization key; it can also be
        expanded to include additional header keys).
        """
        self.region = region
        self.api_root = API_ENVIRONMENTS[region]
        self.api_header = {'Authorization': f"Bearer {api_token}", "Content-Type": "application/json"}
        return None
    
    #
    # Standard API requests for GET, POST, PATCH, and DELETE
    # (mostly tested)
    def api_request(self, req_type, target, url_params=None, payload=None):
        """
        This is a general purpose method for the Workato class that allows an instance of Workato to
        make an API request for a given resource from Workato. You must specify the request type, the
        resource, URL parajeters (if any), and a payload (if there is one). The response is an object
        of the WorkatoResponse class.
        """
        # Might need to comment out this "blank" assignment -- it was added just to initialize the variable 'result' but may create problems
        result = requests.Response
        target = f"{self.api_root}{target}"
        try:
            if req_type == 'get':
                result = requests.get(target, headers=self.api_header, params=url_params, data=payload, verify=False)
            elif req_type == 'post':
                result = requests.post(target, headers=self.api_header, params=url_params, data=payload, verify=False)
            elif req_type == 'put':
                result = requests.put(target, headers=self.api_header, params=url_params, data=payload, verify=False)
            elif req_type == 'patch':
                result = requests.patch(target, headers=self.api_header, params=url_params, data=payload, verify=False)
            elif req_type == 'delete':
                result = requests.delete(target, headers=self.api_header, params=url_params, data=payload, verify=False)
            else:
                raise Exception("Workato.api_request(): Invalid request type.")
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text, # "None", "Log message")
                                   result.json() if result.status_code in [200, 201] else "None", 
                                   generate_response_log_message(result))
        return response
    
    #
    # SPECIALTY FUNCTIONS

    #
    # Create New Workspace (Managed Customer Account)
    # (mostly tested)
    def create_workspace(self, workspace_name, external_id, notification_email):
        """
        Method to create a new managed customer workspace from a Workato OEM account. Requires a name for the new
        workspace, an external ID, and a notification e-mail. Returns an object of the WorkatoResponse class.
        """
        if workspace_name is None or notification_email is None:
            raise InternalOperationError("Workato.create_workspace(): workspace_name or notification_email missing.")
        target = f"{self.api_root}/api/managed_users"
        payload = {'name': workspace_name, 'external_id': external_id, 'notification_email': notification_email}
        try:
            result = requests.post(target, headers={**self.api_header, "content-type": "application/json"}, data=json.dumps(payload), verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text, 
                                   result.json() if result.status_code in [200, 201] else "None", 
                                   generate_response_log_message(result))
        return response
    
    #
    # Add Workspace Collaborator
    # (untested)
    def add_workspace_collaborator(self, name, email, role, workspace_id=None, external_id=None):
        """
        Method to invite a new collaborator to a managed customer workspace. Requires the name, e-mail, and
        role in Workato for the new collaborator, as well as either Workato's own ID for the workspace, or it's
        external ID. Returns an object of the WorkatoResponse class.
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.add_workspace_collaborator(): no workspace or external ID provided.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        target = f"{self.api_root}/api/managed_users/{client_id}/member_invitations"
        payload = json.dumps({'name': name, 'email': email, 'role_name': role})
        try:
            # might need to use headers={**self.api_header, "content-type": "application/json"} as with create_workspace()
            result = requests.post(target, headers=self.api_header, data=payload, verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text, 
                                   result.json() if result.status_code in [200, 201] else "None", 
                                   generate_response_log_message(result))
        return response
    
    #
    # Export RLCM Package
    # (untested)
    def export_package(self, manifest_id, workspace_id=None, external_id=None):
        """
        Method to initialize an export operation for a manifest in the Recipe Life Cycle Management
        console. The operation will trigger the export of the manifest's artifacts as a zip file. The
        method will only trigger the export operation. Use the get_export_status() method to monitor
        the status of the operation and retrieve the download URL when complete. The input parameters
        required are the manifest ID and the Workato workspce ID or external ID for the workspace from
        which the manifest will be exported. The method returns an object of the WorkatoResponse class.
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.export_package(): No workspace or external ID provided for source workspace.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        target = f"{self.api_root}/api/managed_users/{client_id}/exports/{manifest_id}"
        try:
            result = requests.post(target, headers=self.api_header, verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text,
                                       result.json() if result.status_code in [200, 201] else "None",
                                       generate_response_log_message(result))
            
        return response
    
    #
    # Get status of an active manifest export
    # (tested - working)
    def get_export_status(self, package_id, workspace_id=None, external_id=None):
        """
        Monitor an ongoing manifest export operation. The method takes a package ID and either a Workato
        workspace ID or an external ID for the workspace the export is coming from. The method will query
        the status every three seconds until it either reports the export is complete or throws an error.
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.get_export_status(): No workspace or external ID provided.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        target = f"{self.api_root}/api/managed_users/{client_id}/exports/{package_id}"
        try:
            result = requests.get(target, headers=self.api_header, verify=False)
            while result.status_code in [200, 201] and result.json()['result']['status'] not in ['completed', 'failed', 'error', 'stopped']:
                time.sleep(3)
                result = requests.get(target, headers=self.api_header, verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text, 
                                result.json()['result'] if result.status_code in [200, 201] else "None", 
                                generate_response_log_message(result))
        return response

    #
    # Download RLCM Package
    # (tested - working)
    def download_package(self, download_url, local_file):
        """
        This method facilitates downloading a package zip file to a specified local file once
        a manifest export operation has been completed. It must be supplied with the download
        URL provided from the package's status, and a name for the local file. It returns a
        simple log message confirming the package has been downloaded and repeating the local
        file name.
        """
        try:
            data = requests.get(download_url, stream=True, verify=False)
            with open(local_file, 'wb') as of:
                for chunk in data.iter_content(chunk_size=128):
                    of.write(chunk)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            log_message = f"Successfully downloaded package file to {local_file}"
        return log_message
    
    #
    # Import RLCM Package
    # (untested)
    def import_package(self, package_file, folder_id, restart=False, workspace_id=None, external_id=None):
        """
        This method initiates an import operation in the specified workspace. Like `export_package()`, this
        method only triggers the process; you must use `get_import_status()` to monitor the status of the
        import operation. Required inputs are a zip file package of the manifest to be imported, the folder
        ID for the destination folder, and the workspace or external ID for the destination workspace. Optionally,
        you can also supply a `restart` parameter (boolean; defaults to `False`) if you would like to automatically
        restart recipes that are changed during the operation. Returns a WorkatoResponse object.
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.import_package(): no workspace or external ID provided.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        target = f"{self.api_root}/api/managed_users/{client_id}/imports"
        parameters = { 'folder_id': folder_id, 'restart_recipes': restart }
        try:
            package = open(package_file, 'rb')
            result = requests.post(target, params=parameters, headers={**self.api_header, 'Content-Type': 'application/octet-stream'}, data=package, verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text,
                                       result.json() if result.status_code in [200, 201] else "None",
                                       generate_response_log_message(result))
        return response
    
    #
    # Monitor status of manifest import
    # (untested)
    def get_import_status(self, import_id, workspace_id = None, external_id = None):
        """
        Monitor the status of an import operation until the process finishes or fails. Requires the 
        import ID for the operation (from `import_package()`) and either the workspace ID or external
        ID. Returns a WorkatoResponse object.
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.get_import_status(): no workspace or external ID provided.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        target = f"{self.api_root}/api/managed_users/{client_id}/imports/{import_id}"
        try:
            result = requests.get(target, headers=self.api_header, verify=False)
            while result.status_code in [200, 201] and result.json()['status'] not in ['completed', 'failed', 'error']:
                time.sleep(3)
                result = requests.get(target, headers=self.api_header, verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text, 
                                result.json() if result.status_code in [200, 201] else "None", 
                                generate_response_log_message(result))
        return response
    
    #
    # Start or stop a specific recipe
    # (untested)
    def recipe_start_stop(self, operation, recipe_id, workspace_id=None, external_id=None):
        """
        Allows starting and stopping of a specified recipe in a given workspace. You must specify
        the operation (either 'start' or 'stop'), the recipe ID, and either the workspace's Workato
        ID or external ID. Returns a WorkatoResponse object.
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.recipe_start_stop(): no workspace or external ID provided.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        target = f"{self.api_root}/api/managed_users/{client_id}/recipes/{recipe_id}/{operation}"
        try:
            result = requests.put(target, headers=self.api_header, verify=False)
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text,
                                       result.json() if result.status_code in [200, 201] else "None",
                                       generate_response_log_message(result))
        return response
    
    #
    # Retrieve or upsert environment properties
    # (mostly tested)
    def environment_properties(self, operation, workspace_external_id, prefix="", properties=None):
        """
        Allows for retrieving or upserting environment properties in a workspace, depending
        on the specified operation. If `operation` is `"get"`, the method will retrieve all
        environment properties from `workspace_external_id` matching the prefix specified as
        `prefix`. If no prefix is specified, the default value of `""` is used and all extant
        properties in a workspace are retieved. If `operation` is `"upsert"`, the dictionary
        of `properties` is upserted to `workspace_external_id`.
        """
        try:
            if operation == 'get':
                target = f"{self.api_root}/api/managed_users/E{workspace_external_id}/properties?prefix={prefix}"
                print(target)
                result = requests.get(target, headers=self.api_header, verify=False)
            elif operation == 'upsert':
                if type(properties) == dict:
                    target = f"{self.api_root}/api/managed_users/E{workspace_external_id}/properties"
                    result = requests.post(target, data=json.dumps(properties), headers=self.api_header, verify=False)
                else:
                    raise InternalOperationError(f"Workato.environment_properties(): properties argument must be dictionary.")
            else:
                raise InternalOperationError(f"Workato.environment_properties(): invalid operation '{operation}'.")
        except Exception as ex:
            raise InternalOperationError(ex)
        else:
            response = WorkatoResponse(result.status_code, result.headers, result.text, 
                                       result.json() if result.status_code in [200, 201] else "None", 
                                       generate_response_log_message(result))
        return response
    
    #
    # Get folder structure of a workspace
    # (untested)
    def get_folder_structure(self, type, workspace_id=None, external_id=None):
        """
        Returns the folder structure of a specified workspace. You must provide the TYPE --
        being either `project` or `folder` -- and the workspace ID or external ID
        """
        if workspace_id is None and external_id is None:
            raise InternalOperationError("Workato.get_folder_structure(): no workspace or external ID provided.")
        else:
            client_id = workspace_id if workspace_id is not None else f"E{external_id}"
        # Create the directory_structure object
        projects, folders = [], []
        ## STAGE 1: first, we need to get the projects
        #target = f"{self.api_root}/api/managed_users/{client_id}/projects"
        #result = requests.get(target, headers=self.api_header, verify=False)
        #for project in result.json()['result']:
        #    projects.append({"name": project['name'], "id": project['folder_id'], "description": project['description']})
        # STAGE 2: second, we need to get the folders
        target = f"{self.api_root}/api/managed_users/{client_id}/folders"
        result = requests.get(target, headers=self.api_header, verify=False)
        for folder in result.json()['result']:
            folders.append({"name": folder['name'], "id": folder['id']})
        return {"projects": projects, "folders": folders}

    #
    # Generate environment reports
    # (untested)
    def environment_report(self, report_type, workspace_id=None, workspace_external_id=None, report_name=None):
        """
        Returns a JSON report in `response.data` of the requested environment details, specified by
        `report_type`. Available options include `user_roles`, `customers`, `collaborators`, or `connections`.
        If `report_type` is `collaborators`, you must specify either `workspace_id` or `workspace_external_id`
        for the workspace you want to retrieve collaborators from.
        """
        report_endpoins = {
            'user_roles': "/api/roles",
            'customers': "/api/managed_users",
            'collaborators': "/api/managed_users/{workspace}/members",
            'connections': "/api/managed_users/{workspace}/connections"
        }
        if report_type in ['collaborators', 'connections']:
            if workspace_id is None and workspace_external_id is None:
                raise InternalOperationError("Workato.environment_report(): `collaborators` report type requires workspace ID.")
            elif workspace_id is not None:
                target = self.api_root + report_endpoins[report_type].format(workspace=workspace_id)
            else:
                target = self.api_root + report_endpoins[report_type].format(workspace=f"E{workspace_id}")
        else:
            target = f"{self.api_root}{report_endpoins[report_type]}"
        try:
            # RE: "customers" reports
            # How do we determine whether this will result in more than one page for all customers and,
            # if so, how do we handle that?
            result = requests.get(target, headers=self.api_header, verify=False)
            if report_type in ['customers']:
                #report_data = list(result.json()['result'])
                response = WorkatoReport(report_name, result.json()['result'])
                page = 1
                while len(result.json()['result']) == 100:
                    page += 1
                    result = requests.get(target, headers=self.api_header, params={'page': page}, verify=False)
                    #report_data.append(result.json()['result'])
                    response.add_data(result.json()['result'])
            else:
                response = WorkatoReport(report_name, result.json())
        except Exception as ex:
            raise InternalOperationError(ex)
        return response
    
    # Get connector details
    # (untested)
    def get_connector_details(self, type="meta"):
        """
        Returns details about the connector SDKs available in a Workato Embedded subscriptions.
        The `type` must be either "meta" (for connector metadata), "platform" (for platform
        connectors), or "all" (for both connector metadata and platform connectors). Currently,
        only "meta" is supported.
        """
        connector_resources = {
            "meta": "/api/integrations",
            "platform": "/api/integrations/all"
        }
        results = {}
        try:
            if type in ['meta', 'both']:
                target = self.api_root + connector_resources['meta']
                r = requests.get(target, headers=self.api_header, verify=False)
                results['metadata'] = r.json()
            if type in ['platform', 'both']:
                target = self.api_root + connector_resources['platform']
                r = requests.get(target, headers=self.api_header, verify=False)
                results['platofmr'] = r.json()
        except Exception as ex:
            raise InternalOperationError(ex)
        return results
