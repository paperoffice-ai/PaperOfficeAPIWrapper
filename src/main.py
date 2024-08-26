# Standard library imports
import json
import logging
import threading
import os
import re
import shutil
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
import argparse

# Third-party imports
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, format='[ %(asctime)s.%(msecs)05d ] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')

version = "R240807"
border = "=" * 79
print(border)
print(f"\n\tPaperOffice API Wrapper", version)
print(f"\tGitHub: https://github.com/paperoffice-ai/PaperOfficeAPIWrapper")
print(f"\tAPI Documentation: https://app-desktop.paperoffice.com/en/api\n")
print(border + "\n")

# Check if the Python version is at least 3.7
if sys.version_info < (3, 7):
    print("ERROR: Python 3.7 or higher is required.")
    sys.exit(1)
    
    
# Sys exit function with pause
def sys_exit():
    for i in range(20, -1, -1):
        print(f'Exiting in: {i} seconds', end="\r")
        sys.stdout.flush()
        time.sleep(1)
    print("\nExiting now.")  # Move to the next line before exiting
    sys.exit(1)
    

# Set up logging with a rotating file handler
def setup_logging(log_file, env_config):
    log_level = env_config["log_level"]
    max_bytes = env_config["log_file_max_mb"] * 1024 * 1024
    backup_count = env_config["log_file_backup_count"]
        
    # Create a rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    
    # Define a log format
    formatter = logging.Formatter('[ %(asctime)s.%(msecs)05d ] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Set the formatter for the handler
    handler.setFormatter(formatter)
    
    # Create a stream handler to output logs to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Get the root logger
    root_logger = logging.getLogger()
    
    # Set the logging level
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # Add the rotating file handler to the root logger
    root_logger.addHandler(handler)
    
    # Also add a stream handler to output logs to the console
    root_logger.addHandler(stream_handler)
     

# Function to clear relevant environment variables
def clear_env_variables():
    for var in ['API_KEY', 'LOG_LEVEL', 'LOG_FILE_MAX_MB', 'LOG_FILE_BACKUP_COUNT']:
        if var in os.environ:
            del os.environ[var]


# Determine the root path
def get_root_path():
    if getattr(sys, 'frozen', False):  # Check if running as a bundled executable
        root_path = Path(sys.executable).parent
    else:
        root_path = Path(__file__).resolve().parent
    return root_path


# Function to load and validate environment variables from a .env file
def load_env_file(root_path, env_file_name=".env"):

    # Construct the full path to the .env file
    env_file_path = root_path / env_file_name
    
    # Check if the .env file exists at the specified path
    if not env_file_path.exists():
        logging.error(f'The "{env_file_name}" file is missing at {env_file_path}. Please create the file and add your configuration settings.')
        sys_exit()
    
    # Clear relevant environment variables to ensure fresh load
    clear_env_variables() 
        
    # Load the environment variables from the specified .env file
    load_dotenv(dotenv_path=env_file_path)
    
    # Retrieve environment variables and store them in a dictionary
    env_config = {
        "api_key": os.getenv('API_KEY', ''),  # Retrieve the API key, default to empty string if not found
        "log_level": os.getenv('LOG_LEVEL', 'INFO').upper(),  # Retrieve the logging level, default to 'INFO' if not found
        "log_file_max_mb": os.getenv('LOG_FILE_MAX_MB') or 10,  # Retrieve the max log file size in MB, default to 10 MB if not found or empty
        "log_file_backup_count": os.getenv('LOG_FILE_BACKUP_COUNT') or 5  # Retrieve the log file backup count, default to 5 if not found or empty
    }
    
    # Check if the API key is present in the environment variables
    if not env_config['api_key']:
        # Log an error and exit if the API key is missing
        logging.warning('API key missing in the ".env" file. Using free tier.')

    # Validate LOG_LEVEL and default to 'INFO' if invalid
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if env_config["log_level"] not in valid_log_levels:
        logging.info('Invalid LOG_LEVEL in ".env" file. Defaulting to "INFO".')
        env_config["log_level"] = "INFO"   
    
    # Validate LOG_FILE_MAX_MB and default to 10 if invalid
    try:
        env_config["log_file_max_mb"] = int(env_config["log_file_max_mb"])
        if env_config["log_file_max_mb"] <= 0:
            raise ValueError
    except ValueError:
        logging.info('Invalid LOG_FILE_MAX_MB in ".env" file. Defaulting to 10 MB.')
        env_config["log_file_max_mb"] = 10

    # Validate LOG_FILE_BACKUP_COUNT and default to 5 if invalid
    try:
        env_config["log_file_backup_count"] = int(env_config["log_file_backup_count"])
        if env_config["log_file_backup_count"] <= 0:
            raise ValueError
    except ValueError:
        logging.info('Invalid LOG_FILE_BACKUP_COUNT in ".env" file. Defaulting to 5.')
        env_config["log_file_backup_count"] = 5   
        
    logging.info('Environment variables loaded.') 
    
    # Return the dictionary containing the environment configuration
    return env_config


# Check if json is well formatted
def validate_json_keys(json_data) -> None:
    logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Validating json keys.')
    required_folder_keys = {"folder_path", "output_folder", "endpoint"}
    required_endpoint_keys = {"url", "payload"}

    if "folders" not in json_data:
        logging.error(f'Invalid JSON format, "folders" key is missing.')
        sys_exit()

    for folder in json_data["folders"]:
        if not isinstance(folder, dict):
            logging.error(f'Invalid JSON format, invalid key for folder.')
            sys_exit()

        folder_keys = set(folder.keys())
        if not required_folder_keys.issubset(folder_keys):
            logging.error(f'Invalid JSON format, invalid or missing key for folder.')
            sys_exit()

        endpoint = folder.get("endpoint", {})
        if not isinstance(endpoint, dict):
            logging.error(f'Invalid JSON format, invalid "endpoint" key.')
            sys_exit()

        endpoint_keys = set(endpoint.keys())
        if not required_endpoint_keys.issubset(endpoint_keys):
            logging.error(f'Invalid JSON format, invalid or missing key in "endpoint".')
            sys_exit()
                        
    logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - json keys validated.')


# Read and check if valid json
def read_folder_settings_file(root_path):
    folder_settings_file = root_path / "folder_settings.json"
    
    # Check if the configuration file exists
    if not folder_settings_file.exists():
        logging.error('The "folder_settings.json" file is missing. Please create the file and add your configuration settings.')
        sys_exit()
    
    # Load the JSON config file and handle potential errors
    try:
        with open(folder_settings_file, 'r', encoding='utf-8') as config_file:
            folder_settings = json.load(config_file)
    except json.JSONDecodeError as e:
        logging.error(f'Invalid JSON format in "folder_settings.json": {str(e)}')
        sys_exit()
    except Exception as e:
        logging.error(f'An error occurred while reading "folder_settings.json": {str(e)}')
        sys_exit()
        
    validate_json_keys(folder_settings)
    
    logging.info('Folder settings loaded.')
    logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Loaded folder settings: {str(folder_settings)}')
    
    return folder_settings



# APIWrapper Class
class APIWrapper:
    def __init__(self, folder_settings, api_key, tests, tests_amount) -> None:
        self.folder_settings = folder_settings
        self.api_key = api_key
        self.skip_folder = False
        self.total_folders = 0
        self.total_files = 0
        self.threads = []   
             
        """
        --- Tests ---
        tests (bool): Indicates whether benchmark tests are enabled. 
            - When True:
                - Only the first file in the folder will be processed.
                - Files will not be moved.
                - Downloads will be overwritten.
            - Set to False for normal operation.
        
        tests_amount (int): Specifies the number of requests to send if tests are enabled.
            - Note: API credits will still be consumed during tests, so use with caution.
        """
        self.tests = tests
        self.tests_amount = tests_amount
        
        if self.tests:            
            warning_message = f"""
Benchmark mode is enabled.
    - Only the first file in the folder will be processed.
    - Files will not be moved.
    - Downloads will be overwritten.
    - {tests_amount} requests will be sent.
    - API credits will still be consumed during tests, so use with caution.
    Do you wish to continue? (Y/N): """
            
            proceed_benchmark = input(warning_message).strip().lower()
            if proceed_benchmark != 'y':
                print("Benchmark canceled.")
                sys_exit()
            
            logging.info(f'Benchmark mode enabled: Processing {self.tests_amount} requests.')   
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: APIWrapper initialized with provided configuration.')

    
    def process_all_folders(self) -> None:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - process_all_folders')
        for folder in self.folder_settings['folders']:
            folder_configs = {
                "recursive": folder.get("recursive", False),
                "folder_path": folder['folder_path'],
                "output_folder": folder['output_folder'],
                "endpoint": folder['endpoint']
            }
            self.process_folder(folder_configs)
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - process_all_folders')


    # Check if a folder_path exists
    def check_folder_path_exists(self, folder_path) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking if folder exists: {folder_path}')
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logging.warning(f'The folder "{folder_path}" does not exist or is not a directory. Skipping folder.')
            return False
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - Folder "{folder_path}" exists.')
        return True
    
    
    # Check if processed_files_folder exists, if not, create the folder
    def check_and_create_processed_files_folder(self, processed_files_folder):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking if "processed_originals" folder exists')
        
        if not os.path.exists(processed_files_folder):
            try:
                os.makedirs(processed_files_folder)
                logging.info(f'The folder "{processed_files_folder}" did not exist and was created successfully.')
            except Exception as e:
                logging.error(f'Failed to create folder "{processed_files_folder}". Error: {str(e)}. Skipping folder.')
                return False
        elif not os.path.isdir(processed_files_folder):
            logging.warning(f'The path "{processed_files_folder}" exists but is not a directory. Skipping folder.')
            return False
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - Folder "{processed_files_folder}" exists or was created successfully.')
        return True
    
        
    # Check if output_folder exists, if not, create the folder
    def check_and_create_output_folder(self, output_folder) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking if folder exists: {output_folder}')
        
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
                logging.info(f'The folder "{output_folder}" did not exist and was created successfully.')
            except Exception as e:
                logging.error(f'Failed to create folder "{output_folder}". Error: {str(e)}. Skipping folder.')
                return False
        elif not os.path.isdir(output_folder):
            logging.warning(f'The path "{output_folder}" exists but is not a directory. Skipping folder.')
            return False
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - Folder "{output_folder}" exists or was created successfully.')
        return True
    
    
    # Check if input and output folders are the same
    def check_input_output_folder(self, folder_path, output_folder) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking input and output folders are not the same')
        try:
            if folder_path == output_folder:
                logging.warning(f'The output directory "{output_folder}" cannot be the same as the input directory "{folder_path}". Skipping the folder.')
                return False
            return True
        finally:
            logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - Checking input and output folders are not the same')
        
    
    # List all files of the given folder
    def list_files_in_folder(self, folder_path, recursive) -> list:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Listing files in folder: {folder_path}')
        try:
            if recursive:
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Recursively listing files from folder: {folder_path}')
                logging.info(f'Recursively listing files from folder: {folder_path}')

                folder_files_list = []
                for root, dirs, files in os.walk(folder_path):
                    # Skip directories named "processed_originals"
                    dirs[:] = [d for d in dirs if d != "processed_originals"]
                    for file in files:
                        folder_files_list.append(os.path.join(root, file))
            else:
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Listing files from folder: {folder_path}')
                folder_files_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))] 
                if self.tests:
                      folder_files_list = [folder_files_list[0]] * self.tests_amount
                                                    
            
            return folder_files_list
        except Exception as e:
            logging.error(f'Failed to list files in folder "{folder_path}". Error: {str(e)}')
            return []
        finally:
            logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - Listing files in folder: {folder_path}')
            

    # Check response status code
    def check_response_status_code(self, status_code, endpoint_url, file_name, job_id) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking status code for "{file_name}".')
        if not status_code:
            logging.error(f'No status code available. Job-ID: {job_id}')
            return False
        elif status_code == 401:
            logging.error(f'Authentication failed. Status code: {status_code}. Please verify your API key and try again. Job-ID: {job_id}')
            sys_exit()
        elif status_code == 429:
            logging.error(f'Request limit exceeded for endpoint: "{endpoint_url}". Status code: {status_code}. Please try again later or consider upgrading your plan. Job-ID: {job_id}')
            return False        
        
        return True
        

    # Check response status key result
    def check_job_add_response_status_key(self, response_json, endpoint_url, file_name) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking response staus key for "{file_name}".')
        """ 
        Responses: queued, waiting4files, error
        """
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Request response for "{file_name}": {response_json}')
        response_status = response_json["status"]
        try:
            if response_status == "queued":
                return True        
            elif response_status == "waiting4files":
                return True        
            elif response_status == "error":
                response_code = response_json["code"]
                if response_code == 429:
                    logging.error(f'Request limit exceeded for endpoint: "{endpoint_url}". Status code: 429. Please try again later or consider upgrading your plan. Response: {response_json}')
                    return False
                elif response_code == 401:
                    logging.error(f'Authentication failed. Status code: 401. Please verify your API key and try again. Response: {response_json}')
                    sys_exit()
                elif response_code == 421:
                    logging.error(f'Tier limit can not be found. Status code: 421. Please verify your API key and try again. Response: {response_json}')
                    sys_exit()   
                else: 
                    logging.error(f'Unknown error adding new job for "{file_name}". Skipping file. Response: {response_json}')
                    return False
            else:
                logging.error(f'Job start failed for "{file_name}", response status: {response_status}. Skipping file. Response: {response_json}')
                return False 
        except Exception as e:
            logging.error(f'Request error for endpoint: "{endpoint_url}". File "{file_name}". Response: {response_json}')
            return False
            

    # 1. Send Request Job/add
    def send_request_job_add(self, endpoint, file_name):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Send request for "{file_name}"') 
        endpoint_url = endpoint["url"]   
        
        payload = endpoint["payload"] if endpoint["payload"] else {}

        if type(payload) != dict:
            logging.warning(f'Invalid payload: "{str(payload)}" in "folder_settings.json", sending empty payload.') 
            payload = {}
             
        payload["paperoffice_device_origin"] = "paperoffice_api_wrapper"
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Payload for "{file_name}": {str(payload)}')     
        
        headers = {}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        for i in range(3):
            try:
                response = requests.post(endpoint_url, data=payload, headers=headers, timeout=10) 
                response_json = response.json() 
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Successfully sent request to {endpoint_url} for "{file_name}"')
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Response status code: {response.status_code} for "{file_name}"')
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Response: {response_json} for "{file_name}"')

                return response_json, response.status_code
            
            except Exception as e:
                if i == 2:
                    logging.error(f'Failed to send request to "{endpoint_url}" with status code: {response.status_code} for "{file_name}". Message: {str(e)}')
                    return None, None
                time.sleep(1)
            
  
    # Check response status key result
    def check_job_upload_response_status_key(self, response_json, file_name, job_id) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking response staus key for "{file_name}".')
        """ 
        Possible status responses: queued,  error
        """
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Request response for "{file_name}": {response_json}')
        response_status = response_json["status"]
        try:
            if response_status == "queued":
                return True        
            elif response_status == "error":
                response_code = response_json["code"]
                if response_code == 429:
                    logging.error(f'Request limit exceeded for endpoint: "job/upload". Status code: 429. Please try again later or consider upgrading your plan. Job-ID: {job_id}. Response: {response_json}')
                    return False
                elif response_code == 401:
                    logging.error(f'Authentication failed. Status code: 401. Please verify your API key and try again. Job-ID: {job_id}. Response: {response_json}')
                    sys_exit()
                elif response_code == 421:
                    logging.error(f'Tier limit can not be found. Status code: 421. Please verify your API key and try again. Job-ID: {job_id}. Response: {response_json}')
                    sys_exit()  
                else: 
                    logging.error(f'Unknown error uploading "{file_name}". Skipping file. Job-ID: {job_id}. Response: {response_json}')
                    return False 
            else:
                logging.error(f'Job upload failed for "{file_name}", response status: {response_status}. Message: {response_json["message"]} Skipping file. Job-ID: {job_id}. Response: {response_json}')
                return False 
        except Exception as e:
            logging.error(f'Request error for "{file_name}", endpoint: "job/upload". Job-ID: {job_id}. Response: {response_json}')
            return False
  
  
    # 2. Send Request Job/Upload
    def send_request_job_upload(self, endpoint_url, file, file_name, job_id):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Send request upload for "{file_name}".')        
                
        headers = {}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        files = {
            "job_files_0": open(file, 'rb')
        }            
            
        try:
            for i in range(3): 
                try:
                    response = requests.post(endpoint_url, headers=headers, files=files, timeout=10)
                    response_json = response.json()
                    logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: "{file_name}" successfully uploaded to: {response.url}')
                    logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Response status code: {response.status_code} for "{file_name}".')
                    logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Response for "{file_name}": {response_json}')
                
                    return response_json, response.status_code
                
                except Exception as e:
                    if i == 2:
                        logging.error(f'Failed to send request for "{file_name}" to "{endpoint_url}". Job-ID: {job_id}. Message: {str(e)}')
                        return None, None
                    time.sleep(1)        
        finally:
            files["job_files_0"].close()
        

    # Check response status key result
    def check_job_status_response_status_key(self, response_json, file_name, job_id):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Checking response staus key for "{file_name}".')
        """ 
        Status options: 'queued', 'waiting4files', 'processing', 'completed', 'failed', 'timeout'
        """
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Request response for "{file_name}": {response_json}')
        response_status = response_json["status"]
        try:                    
            if response_status == "completed":
                return "completed"        
            elif response_status == "failed":
                return "failed"               
            elif response_status == "processing":
                return "processing"
            elif response_status == "queued":
                return "queued"
            elif response_status == "error":                
                if "RATE_LIMIT_EXCEEDED" in response_json["message"]:
                    return "processing"
                
                response_code = response_json["code"]
                if response_code == 429:
                    logging.error(f'Request limit exceeded for endpoint: "job/upload". Status code: 429. Please try again later or consider upgrading your plan. Job-ID: {job_id}. Response: {response_json}')
                    return False
                elif response_code == 401:
                    logging.error(f'Authentication failed. Status code: 401. Please verify your API key and try again. Job-ID: {job_id}. Response: {response_json}')
                    sys_exit()
                elif response_code == 421:
                    logging.error(f'Tier limit can not be found. Status code: 421. Please verify your API key and try again. Job-ID: {job_id}. Response: {response_json}')
                    sys_exit()  
                else: 
                    logging.error(f'Unknown error checking job status for "{file_name}". Skipping file. Mesage: {response_json["message"]}. Job-ID: {job_id}. Response: {response_json}')
                    return False
            else:
                logging.error(f'Job upload failed for "{file_name}", response status: {response_status}. Message: {response_json["message"]} Skipping file. Job-ID: {job_id}. Response: {response_json}')
                return False 
        except Exception as e:
            logging.error(f'Request error for "{file_name}", endpoint: "job/status". Job-ID: {job_id}. Response: {response_json}')
            return False


    # 3. Send Request Job/status
    def send_request_job_status(self, endpoint_url, file_name, job_id):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Send request Status for "{file_name}"') 

        headers = {}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for i in range(3):
            try:
                response = requests.get(endpoint_url, headers=headers, timeout=10)
                response_json = response.json()
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Job status for "{file_name}": {response.json()["status"]}')
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Response status code for "{file_name}": {response.status_code}')
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Response for "{file_name}": {response_json}')
            
                return response_json, response.status_code
            
            except Exception as e:
                if i == 2:
                    logging.error(f'Failed to get job status for "{file_name}". Job-ID: {job_id}. Message: {str(e)}')
                    return None, None
                time.sleep(1)
                    

    # 4. Download processed job files
    def download_processed_job_files(self, downloadlink, output_folder, original_file_name, job_id) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Downloading file(s) for processed "{original_file_name}".') 
        
        try:
            response = requests.get(downloadlink, allow_redirects=True)
            if response.status_code == 200:
                # Try to get the filename from the Content-Disposition header
                content_disposition = response.headers.get('content-disposition')
                if content_disposition:
                    filename = re.findall('filename="(.+)"', content_disposition)
                    if filename:
                        file_name = filename[0].encode('latin1').decode('utf-8')
                    else:
                        file_name = original_file_name
                else:
                    file_name = original_file_name
                
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
                file_name = original_file_name if self.tests else f'{timestamp}_{file_name}'            
                full_path_filename = Path(output_folder) / file_name
                with open(full_path_filename, 'wb') as file:
                    file.write(response.content)
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: "{file_name}" downloaded successfully for "{original_file_name}".')
                return True
            else:
                logging.error(f'Failed to download "{file_name}" for "{original_file_name}". Job ID: {job_id}')
                return False
        
        except Exception as e:
            logging.error(f'Failed to download "{file_name}" for "{original_file_name}". Job ID: {job_id}')
            return False

    
    # Move processed file to processed_originals" folder
    def move_file_with_timestamp(self, file, file_name, processed_files_folder):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - Moving file: {file_name}') 
        
        if not self.tests:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
                                
            # Create the new filename with timestamp
            new_filename = f"{timestamp}_{file_name}"
            
            # Move the file with the new filename
            destination = str(Path(processed_files_folder) / new_filename)
        
            shutil.move(file, destination)  
        logging.info(f'Successfully processed "{file_name}".')              
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - File {file_name} moved successfuly.') 


    # Process file in individual thread for parallel processing
    def process_file_in_thread(self, response_json, file, file_name, processed_files_folder, output_folder) -> str:
        # 2. Upload file
        # Get assigned server and job ID
        job_assigned_api_endpoint = response_json["job_assigned_api_endpoint"]
        job_id = response_json["job_id"]            
        endpoint_url = f'https://{job_assigned_api_endpoint}/V5/job/upload/{job_id}'
        response_json, status_code = self.send_request_job_upload(endpoint_url, file, file_name, job_id)
        
        if not status_code:
            return
        
        if not self.check_response_status_code(status_code, endpoint_url, file_name, job_id):
            self.skip_folder = True
            return
        
        if self.check_job_upload_response_status_key(response_json, file_name, job_id):
            logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: "{file_name}" queued')
        else:
            return
        
        
        # 3. Check job status
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Checking job status for "{file_name}".')
        endpoint_url = f'https://{job_assigned_api_endpoint}/V5/job/status/{job_id}'
        
        time.sleep(0.5)
        max_retries = 30
        for i in range(max_retries):                
            response_json, status_code = self.send_request_job_status(endpoint_url, file_name, job_id)
            
            if not status_code:
                return
            
            if not self.check_response_status_code(status_code, endpoint_url, file_name, job_id):
                self.skip_folder = True
                return 
            
            
            job_response_status = self.check_job_status_response_status_key(response_json, file_name, job_id)
            if job_response_status == "queued": 
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: "{file_name}" queued, waiting for free slot.')
            elif job_response_status == "processing":
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: "{file_name}" is being processed.')
            elif job_response_status == "failed":
                logging.error(f'"{file_name}" processing has failed please try again. Job ID: {job_id}')
                return
            elif job_response_status == "completed":
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: "{file_name}" processing completed. Proceed to downlad.')
                downloadlink = response_json["downloadlink"]
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Downloadlink for "{file_name}": {downloadlink}')
                break
            else:
                logging.error(f'"{file_name}" processing error. Skipping file, please try again. Response: Job ID: {job_id}')
                return
            
            if i == max_retries - 1 :
                logging.error(f'"{file_name}" processing is taking too long. Skipping file, please try again. Job ID: {job_id}')
                return                    
            
            
            # Get next_call_in_seconds
            next_call_in_seconds = 5 if self.tests else response_json["next_call_in_seconds"]
            logging.info(f'Next job status check for "{file_name}" in {next_call_in_seconds} seconds.')
            logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Check job status interval for API key is {next_call_in_seconds} seconds.')
            
            time.sleep(next_call_in_seconds)
            time.sleep(0.3)              
        
        # 4. Download file
        move_processed_file = False
        if downloadlink:                
            if self.download_processed_job_files(downloadlink, output_folder, file_name, job_id):
                move_processed_file = True
        else:
            logging.error(f'File download-link not available for "{file_name}". skipping file. Job ID: {job_id}')
            return
        
        
        if move_processed_file:    
            self.move_file_with_timestamp(file, file_name, processed_files_folder)
        
        # Add 1 to total processed files
        self.total_files += 1


    # Check remaining requests before continuing
    def check_remaining_requests(self, remaining_requests) -> bool:
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - check_remaining_requests.')
        
        time_mapping = {
            "1_minute": 60,
            "1_hour": 3600,
        }

        if not remaining_requests:
            logging.error(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Can not retrieve remaining request - continue.')
            return True
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Remaining requests: {str(remaining_requests)}')
        
        try:
            time_to_wait = 0.0
            for key, value in remaining_requests.items():                
                if value == 0.0:
                    if key in time_mapping:
                        time_to_wait = time_mapping[key]
                        logging.info(f'Request limit reached for {key}. Pausing execution for {time_to_wait} seconds to comply with rate limits.')                    
                    else:
                        logging.warning(f'Request limit reached for {key}. Please try again after the specified time. Exiting script.')
                        return False
             
            if time_to_wait > 0.0:       
                for i in range(time_to_wait, -1, -1):
                    print(f'Time remaining until next request: {i} seconds', end="\r")
                    sys.stdout.flush()
                    time.sleep(1)
            return True
        
        except Exception as e:
            logging.error(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: {str(e)}') 
            return True
            

    # Process files
    def process_files(self, folder_files_list, endpoint, processed_files_folder, output_folder) -> None:
        debug_files_list = '' if self.tests else folder_files_list
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - process_files: {debug_files_list}') 
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Endoint parameters: {endpoint}') 
        
        for file in folder_files_list:
            if self.skip_folder:
                self.skip_folder = False
                break
            file_name = Path(file).name
            logging.info(f'Processing file: "{file_name}".')
            
            # 1. Add job
            response_json, status_code = self.send_request_job_add(endpoint, file_name)
            try:
                job_id = response_json['job_id']
            except:
                job_id = 'None'
            
            if not status_code:
                continue
            
            if not self.check_response_status_code(status_code, endpoint["url"], file_name, job_id):
                break        
            
            # check response status key
            if self.check_job_add_response_status_key(response_json, endpoint["url"], file_name):
                logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Job waiting for file "{file_name}".')
            else:
                continue
            
            # Run each file in individual thread
            thread_name = f'thread_{file_name}'
            thread = threading.Thread(target=self.process_file_in_thread, args=(response_json, file, file_name, processed_files_folder, output_folder), name=thread_name)
            self.threads.append(thread)
            thread.start()    
            
            # Check remaining requests
            remaining_requests = response_json.get("remaining_requests", None)
            if not self.check_remaining_requests(remaining_requests):
                break            
                    
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - All files processed from folder.')
            

    def process_folder(self, folder_configs):
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: START - process_folder')
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Processing folder details: "{str(folder_configs)}"')
        logging.info(f'Processing folder: "{str(folder_configs["folder_path"])}"')
        
        folder_path = Path(folder_configs["folder_path"])
        recursive = folder_configs["recursive"]

        output_folder = Path(folder_configs["output_folder"])
        endpoint = folder_configs["endpoint"]
        
        if not self.check_input_output_folder(folder_path, output_folder):
            return
        
        if not self.check_folder_path_exists(folder_path):
            return
        
        processed_files_folder = folder_path / "processed_originals"
        if not self.check_and_create_processed_files_folder(processed_files_folder):
            return
              
        if not self.check_and_create_output_folder(output_folder):
            return
        
        folder_files_list = self.list_files_in_folder(folder_path, recursive)
        
        # add 1 to total_folders
        self.total_folders += 1
        
        self.process_files(folder_files_list, endpoint, processed_files_folder, output_folder)
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: END - process_folder')      
        

    def format_processing_time(self, total_seconds):
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"
        else:
            return f"{seconds:.2f} second{'s' if seconds != 1 else ''}"



if __name__ == "__main__":
    try:   
        parser = argparse.ArgumentParser(description="Args only for activating tests for bencmarks.")
        parser.add_argument('--tests', action='store_true', help="Enable tests (default: False)")
        parser.add_argument('--tests-amount', type=int, default=0, help="Specify the number of tests to run (default: 0)")
        args = parser.parse_args()  
           
        start_time = time.time()
        start_datetime = datetime.now()        
        
        root_path = get_root_path()
        env_config = load_env_file(root_path)              
        setup_logging(root_path / "process.log", env_config)
        logging.info('Processing started')       
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Debugging application flow - START')
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Loaded environment variables: {str(env_config)}')
        folder_settings = read_folder_settings_file(root_path)
          
        
        # Initialize the APIWrapper class
        aw = APIWrapper(folder_settings, env_config["api_key"], args.tests, args.tests_amount)        
        aw.process_all_folders()
        
        # Join all threads and wait for all threads to finish
        for thread in aw.threads:
            thread.join()   
        
        end_time = time.time()
        end_datetime = datetime.now() 
        # Calculate the total processing time
        total_time = end_time - start_time  
        
        formatted_time = aw.format_processing_time(total_time)
        
        # Log the message with timing information
        logging.info(
            f"Processing complete:\n"
            f"\t- {aw.total_files} file(s) in {aw.total_folders} folder(s) have been processed.\n"
            f"\t- Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"\t- End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"\t- Total processing time: {formatted_time}.\n"
            f'\t- Please refer to the "process.log" file for detailed results and any potential issues.'
        ) 
        
        for i in range(10, -1, -1):
            print(f'Exiting in: {i} seconds', end="\r")
            sys.stdout.flush()
            time.sleep(1)
        
        logging.debug(f'{logging.currentframe().f_code.co_name}:{logging.currentframe().f_lineno}: Debugging application flow - END')
    except Exception as e:
        logging.critical(f'An unexpected error occurred during the execution of the script. Message: {str(e)}')
        sys_exit()
        
