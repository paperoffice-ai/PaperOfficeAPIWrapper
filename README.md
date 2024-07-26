# PaperOfficeAPIWrapper

**PaperOfficeAPIWrapper** is a streamlined tool designed to automate file processing via API requests. Users can configure multiple folders to be processed, each with its own API endpoint. Configuration details, including folder paths and API endpoints, are specified in the `api_file_processor_config.json` file. Each file within the configured folders is sent to the designated API for processing, with results saved to specified output folders. This tool simplifies bulk file processing, making it efficient and customizable for various use cases.


### Getting Started

#### Prerequisites
- Python 3.7+
- pip

#### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/paperoffice-ai/PaperOfficeAPIWrapper.git
   cd PaperOfficeAPIWrapper
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```


### Usage

#### Configuration

1. **Edit the `edit.env` file:**

   Edit the `edit.env` file in the `src` folder with your API key and configuration, then rename it to `.env`:

   ```bash
   mv src/edit.env src/.env
   ```

   For reference, this is the `edit.env` file:

   ```plaintext
   API_KEY=
   LOG_LEVEL=INFO
   LOG_FILE_MAX_MB=10
   LOG_FILE_BACKUP_COUNT=5
   ```

   **Explanation:**
   - **API_KEY**: If no API key is provided, the script will use our free tier.
   - **LOG_LEVEL**: Log level default is `INFO`.
   - **LOG_FILE_MAX_MB**: Maximum log file size is `10 MB` by default.
   - **LOG_FILE_BACKUP_COUNT**: Default backup count for log files is `5`.

2. **Configure the `api_file_processor_config.json` file:**

   Ensure your configuration file (`api_file_processor_config.json`) in the `src` folder is set up as shown below. This file specifies the folders to process and the API endpoints to use.

   ```json
   {
       "folders": [
           {
               "folder_path": "..\\tests\\input_folder",
               "output_folder": "..\\tests\\output_folder",
               "endpoint": {
                   "url": "https://api-dev.paperoffice.com/V5/job/add/pdfstudio___pdf_to_text",
                   "job_instructions_json": {"language":"en","txt":true,"type":"analog"}
               }
           }
       ]
   }
   ```

   **Explanation:**
   - **folder_path**: Path to the folder containing files to process.
   - **output_folder**: Path to the folder where processed files will be saved.
   - **url**: API endpoint URL.
   - **job_instructions_json**: JSON object containing specific instructions for the API job.

3. **Run the script:**

   After configuring the `.env` and `api_file_processor_config.json` files, run the script:

   ```bash
   python src/main.py
   ```

For Windows executable:

```bash
windows/your_script.exe
```

## Development
Development and experimental features can be tested in the `dev` folder.

## Testing
How to run tests:

```bash
pytest tests/
```

## License
Include your project's license information here.
