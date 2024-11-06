from flask import Flask, render_template, request, send_file, flash
import os
import sys
from werkzeug.utils import secure_filename
import subprocess
import uuid
import platform
import ctypes
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flashing messages

# Configure upload folder using absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'converted')
ALLOWED_EXTENSIONS = {'mkv'}

# Ensure directories exist with proper permissions
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)
    # Set proper permissions
    if platform.system() == 'Windows':
        try:
            os.chmod(folder, 0o777)
        except Exception as e:
            logger.error(f"Failed to set permissions for {folder}: {e}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max-limit

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_ffmpeg():
    """Find FFmpeg executable in various locations"""
    possible_paths = [
        r'C:\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
        os.path.join(BASE_DIR, 'ffmpeg', 'bin', 'ffmpeg.exe'),
        'ffmpeg'
    ]
    
    for path in possible_paths:
        try:
            if os.path.isfile(path):
                # Test if we can actually run it
                subprocess.run([path, '-version'], 
                             capture_output=True, 
                             check=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
                logger.info(f"Found working FFmpeg at: {path}")
                return path
        except Exception as e:
            logger.warning(f"Tried FFmpeg at {path}, but failed: {e}")
            continue
    
    return None

# Find FFmpeg at startup
FFMPEG_PATH = find_ffmpeg()
if not FFMPEG_PATH:
    logger.error("FFmpeg not found in any standard location!")
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_mkv_to_mp4(input_path, output_path):
    """Convert MKV to MP4 using FFmpeg with proper error handling"""
    if not FFMPEG_PATH:
        logger.error("FFmpeg not found!")
        return False

    try:
        command = [
            FFMPEG_PATH,
            '-i', input_path,
            '-codec', 'copy',
            '-y',  # Overwrite output file if it exists
            output_path
        ]
        
        logger.info(f"Running conversion command: {' '.join(command)}")
        
        # Run conversion with CREATE_NO_WINDOW flag
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        logger.info("Conversion completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if not FFMPEG_PATH:
            flash('FFmpeg is not properly installed. Please check the installation.', 'error')
            return render_template('index.html')
            
        if 'file' not in request.files:
            flash('No file part', 'error')
            return render_template('index.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return render_template('index.html')
        
        if file and allowed_file(file.filename):
            try:
                unique_filename = str(uuid.uuid4())
                input_filename = secure_filename(f"{unique_filename}.mkv")
                output_filename = f"{unique_filename}.mp4"
                
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                
                logger.info(f"Saving uploaded file to: {input_path}")
                file.save(input_path)
                
                if convert_mkv_to_mp4(input_path, output_path):
                    try:
                        os.remove(input_path)
                    except Exception as e:
                        logger.warning(f"Failed to remove input file: {e}")
                    
                    return send_file(output_path, 
                                   as_attachment=True,
                                   download_name=f"{file.filename[:-4]}.mp4")
                else:
                    flash('Conversion failed. Please check the logs.', 'error')
                    return render_template('index.html')
                    
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                flash(f'Error processing file: {str(e)}', 'error')
                return render_template('index.html')
                
    return render_template('index.html')

if __name__ == '__main__':
    if platform.system() == 'Windows' and not is_admin():
        logger.warning("Application not running with admin privileges. Some features might not work.")
        
    if not FFMPEG_PATH:
        logger.error("FFmpeg not found! Please install FFmpeg and add it to PATH")
    else:
        logger.info(f"Using FFmpeg from: {FFMPEG_PATH}")
        
    app.run(debug=True)