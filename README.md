# MKV to MP4 Converter

A simple web application built with Flask that allows users to convert MKV video files to MP4 format.

## Features

- Web-based interface for file upload
- Converts MKV files to MP4 format using FFmpeg
- Automatic file download after conversion
- Clean interface with progress feedback

## Requirements

- Python 3.8 or higher
- FFmpeg
- Flask

## Installation

1. First, ensure you have FFmpeg installed on your system:

   ### For Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   ### For macOS (using Homebrew):
   ```bash
   brew install ffmpeg
   ```

   ### For Windows:
   Download FFmpeg from the official website and add it to your system PATH.

2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd mkv-to-mp4-converter
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
## Verify FFmpeg Installation & Find FFmpeg executable in various locations

## Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. Click the "Choose File" button and select an MKV file
2. Click "Convert to MP4"
3. Wait for the conversion to complete
4. The converted MP4 file will automatically download when ready

## Project Structure
```
mkv-to-mp4-converter/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── uploads/
└── converted/
```

## Requirements.txt Content
```
Flask==2.0.1
Werkzeug==2.0.1
```

## Notes

- The application automatically creates `uploads` and `converted` directories if they don't exist
- Uploaded MKV files are automatically deleted after conversion
- Converted MP4 files remain in the `converted` directory until manually cleaned
- Make sure you have enough disk space for both the uploaded and converted files
