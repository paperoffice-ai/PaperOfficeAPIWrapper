![Static Badge](https://img.shields.io/badge/python-blue?style=flat&logo=python&logoColor=%23ffffff) ![Version](https://img.shields.io/badge/License-Non%20Commercial-orange) ![Version](https://img.shields.io/badge/version-R247275-green)

# PaperOfficeAPIWrapper

## Table of Contents
1. [Overview](#overview)
   - [Key Features](#key-features)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Quick Start](#quick-start)
3. [Usage Guide](#usage-guide)
   - [Configuration](#configuration)
     - [Set Up Environment Variables](#1-set-up-environment-variables)
     - [Configure API and Folder Settings](#2-configure-api-and-folder-settings)
   - [Running the Script](#running-the-script)
4. [Troubleshooting](#troubleshooting)
5. [License](#license)

## Overview

**PaperOfficeAPIWrapper** is a powerful utility designed to streamline file processing through automated API interactions. It enables efficient management and processing of files across multiple directories, each with its own dedicated API endpoint.

This versatile Python script can be run on any platform, including Linux, macOS, and Windows. For Windows users, a pre-compiled executable is also available for convenience.

- Run the Python script on Linux, macOS, or Windows
- Available as a pre-compiled [Windows executable](https://github.com/paperoffice-ai/PaperOfficeAPIWrapper/releases/download/R247275/com.paperoffice.apiwrapper.R247275.exe)
- Access to multiple PaperOffice endpoints, including:
  - PDF Studio
  - Image Studio
  - Vision API
  - Creator API

For a complete list of available endpoints, please refer to our [API documentation](https://app-desktop.paperoffice.com/en/api).

### Key Features

- **Cross-Platform Compatibility**: Run the Python script on Linux, macOS, or Windows
- **Windows Executable**: Pre-compiled version available for easy use on Windows systems
- **Multi-folder Processing**: Configure and process files from multiple input folders
- **Customizable API Endpoints**: Each folder can be linked to a specific API endpoint for tailored processing
- **Automated Workflow**: Files are automatically sent to designated APIs and results are saved to specified output locations
- **Configurable**: Easy-to-use JSON configuration file for setting up folders and API endpoints
- **Flexible Output Handling**: Processed files can be saved to custom output directories
- **Error Handling**: Robust error management to ensure smooth operation even with large batches of files

<img alt="PaperOfficeAPIWrapper" src="https://github.com/user-attachments/assets/d328fd15-a9d6-4501-b3d1-8d786362e4f9">

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Installation

1. **Clone the Repository**

   Open a terminal and run:

   ```bash
   git clone https://github.com/paperoffice-ai/PaperOfficeAPIWrapper.git
   cd PaperOfficeAPIWrapper
   ```

2. **Set Up a Virtual Environment**

   Create and activate a virtual environment to isolate the project dependencies:

   For Unix-based systems (Linux, macOS):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   For Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   With the virtual environment activated, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Quick Start

1. Configure your environment variables in `src/.env` (see Configuration section for details).
2. Set up your folder and API configurations in `src/api_file_processor_config.json`.
3. Run the main script:

   ```bash
   python src/main.py
   ```


# Usage Guide

## Configuration

### 1. Set Up Environment Variables

Edit the `edit.env` file in the `src` folder with your API key and preferred settings, then rename it to `.env`:

```bash
mv src/edit.env src/.env
```

Example `edit.env` file:

```plaintext
API_KEY=your_api_key_here
LOG_LEVEL=INFO
LOG_FILE_MAX_MB=10
LOG_FILE_BACKUP_COUNT=5
```

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Your API key. If not provided, the script will use the free tier. | None |
| `LOG_LEVEL` | Logging verbosity level | `INFO` |
| `LOG_FILE_MAX_MB` | Maximum size of each log file in megabytes | `10` |
| `LOG_FILE_BACKUP_COUNT` | Number of backup log files to keep | `5` |

### 2. Configure API and Folder Settings

Modify the `api_file_processor_config.json` file in the `src` folder to specify input/output folders and API endpoints. The configuration supports multiple folders, each with its own input/output paths and API endpoint.


#### Example Configuration:

```json
{
    "folders": [
        {
            "folder_path": "/path/to/input_folder1",
            "output_folder": "/path/to/output_folder1",
            "endpoint": {
                "url": "https://api-dev.paperoffice.com/V5/job/add/pdfstudio___pdf_to_text",
                "job_instructions_json": {"language":"en"}
            }
        },
        {
            "folder_path": "/path/to/input_folder2",
            "output_folder": "/path/to/output_folder2",
            "endpoint": {
                "url": "https://api.paperoffice.com/V5/job/add/pdfstudio___pdf_to_searchable_pdf",
                "job_instructions_json": {"language":"en"}
            }
        }
    ]
}
```

#### Path Formatting:

- **Unix-based Systems (Linux, macOS)**: Use forward slashes (`/`) in your paths.
  ```json
  "folder_path": "/home/user/my_input_folder"
  ```

- **Windows**: Use either of these formats:
  1. Double backslashes:
     ```json
     "folder_path": "C:\\Users\\user\\my_input_folder"
     ```
  2. Forward slashes (also supported in Windows):
     ```json
     "folder_path": "C:/Users/user/my_input_folder"
     ```

#### Configuration Fields:

| Field | Description |
|-------|-------------|
| `folder_path` | Directory containing files to process |
| `output_folder` | Directory where processed files will be saved |
| `url` | API endpoint URL for processing |
| `job_instructions_json` | Specific instructions for the API job (e.g., language settings) |


**Note:** 
- Successfully processed files are moved to an `api_processed_files` subfolder within the input folder.
- Ensure you have read/write permissions for all specified folders.
- For more examples, refer to `api_file_processor_config_example.json` in the `src` folder.
- **Important:** For a comprehensive list of all available endpoints and `job_instructions_json` parameters, please refer to our API documentation at: https://app-desktop.paperoffice.com/en/api

## Running the Script

After configuring the `.env` and `api_file_processor_config.json` files, execute:

### For Unix-based Systems (Linux, macOS)


```bash
python3 src/main.py
```

### For Windows Users

```bash
python src/main.py
```

A compiled executable [com.paperoffice.apiwrapper.R247275.exe](https://github.com/paperoffice-ai/PaperOfficeAPIWrapper/releases/download/R247275/com.paperoffice.apiwrapper.R247275.exe) is available inside the windows directory. To use this:

1. Navigate to the `windows` directory.
2. Download `com.paperoffice.apiwrapper.<release>.exe`, `edit.env`, and `api_file_processor_config.json`.
3. Place all files in the same folder.
4. Configure `edit.env` and `api_file_processor_config.json` as described above.
5. Run `com.paperoffice.apiwrapper.<release>.exe`.

## Troubleshooting

- Ensure all configuration files are in the correct locations.
- Verify that your API key is valid and correctly entered in the `.env` file.
- Check that the specified input and output folders exist and are accessible.
- Review the log files for any error messages or warnings.
- If you're unsure about the configuration format, refer to `api_file_processor_config_example.json` for guidance.



## License
**Custom Non-Commercial License**

Copyright (c) 2024 PaperOffice Limited Europe

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to use, copy, modify, merge, and distribute the Software for non-commercial purposes only, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

2. The Software may not be used for commercial purposes, including but not limited to selling the Software, selling services that utilize the Software, or incorporating the Software into a commercial product.

3. Modifications to the Software must be clearly marked as such and must not be misrepresented as the original Software.

4. No person or organization may claim endorsement or affiliation with the original authors or copyright holders without specific prior written permission.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
