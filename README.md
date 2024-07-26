# PaperOffice_API_File_Processor

## Description
A brief description of your project.

## Installation
Instructions to install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration
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

### Explanation:
- **API_KEY**: If no API key is provided, the script will use our free tier.
- **LOG_LEVEL**: Log level default is `INFO`.
- **LOG_FILE_MAX_MB**: Maximum log file size is `10 MB` by default.
- **LOG_FILE_BACKUP_COUNT**: Default backup count for log files is `5`.

## Usage
How to use the project:

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
```

This setup provides clear instructions on how to configure the environment by editing and renaming the `edit.env` file.