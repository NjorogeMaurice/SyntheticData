import io
import os

from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import pandas as pd
import requests

from SyntheticData.main import gen_synthetic_data
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

# Configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the uploaded file is allowed based on its extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request has a file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # Check if the file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check if the file has a valid extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only CSV or XLSX files are allowed.'}), 400

    # Save the file
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    try:
        synthetic_df = gen_synthetic_data(data)
        # Save the synthetic data to a buffer as a CSV
        buffer = io.StringIO()
        synthetic_df.to_csv(buffer, index=False)
        buffer.seek(0)

        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            as_attachment=True,
            download_name='synthetic_data.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/upload-url', methods=['POST'])
def upload_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided.'}), 400


    url = data['url']
    try:
        # Download the file from the URL
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download file from the provided URL.'}), 400

        # Write the file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Determine file type and validate
        filename = url.split('/')[-1]
        if not allowed_file(filename):
            os.unlink(temp_file_path)  # Clean up
            return jsonify({'error': 'Unsupported file type. Please provide a CSV or Excel file.'}), 400

        # Process the file
        if filename.endswith('.csv'):
            df = pd.read_csv(temp_file_path)
            synthetic_df = gen_synthetic_data(df)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(temp_file_path)
            synthetic_df = gen_synthetic_data(df)

        os.unlink(temp_file_path)  # Clean up the temp file

        buffer = io.StringIO()
        synthetic_df.to_csv(buffer, index=False)
        buffer.seek(0)

        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            as_attachment=True,
            download_name='synthetic_data.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({'error': f'Error processing URL: {str(e)}'}), 500


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
