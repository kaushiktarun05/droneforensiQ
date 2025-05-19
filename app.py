from flask import Flask, request, render_template, flash, redirect, url_for, send_file, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from decode import checkType  # Assuming checkType handles conversion
from csv_parse import fill_missing_values
from math import ceil
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = "uploads"
CSV_FOLDER = "csv"  # Storing converted CSV files in root/csv
ROWS_PER_PAGE = 100

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER

def clear_directories():
    """Deletes all files in uploads and csv folders before processing a new file."""
    for folder in [UPLOAD_FOLDER, CSV_FOLDER]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Delete files and links
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        clear_directories()  # Clean directories before saving the new file

        if 'file' not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("No selected file", "error")
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            output_path = os.path.join(app.config['CSV_FOLDER'])
            os.makedirs(output_path, exist_ok=True)
            
            result = checkType(file_path, output_path, "")

            csv_output_file = f"{output_path}/{filename}_output.csv"
            fill_missing_values(csv_output_file, CSV_FOLDER)
            
            flash(f"File successfully converted and saved at {csv_output_file}", "success")
            return redirect(url_for('dashboard'))
    
    return render_template('index.html')

# @app.route('/view_csv')
# def view_csv():
#     """Displays the most recent CSV file as a DataFrame without extra newlines."""
#     files = [f for f in os.listdir(CSV_FOLDER) if f.endswith('.csv')]
    
#     if not files:
#         flash("No CSV file available to display.", "error")
#         return redirect(url_for('upload_file'))
    
#     latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(CSV_FOLDER, f)))
#     csv_path = os.path.join(CSV_FOLDER, latest_file)
    
#     df = pd.read_csv(csv_path, engine="python").fillna("")  # Replace NaN with empty strings
#     table_html = df.to_html(classes='table table-striped', index=False, escape=False)
    
#     return render_template('view_csv.html', table=table_html, title="CSV Preview")


@app.route('/view_csv')
def view_csv():
    """Displays the most recent CSV file as a paginated DataFrame."""
    files = [f for f in os.listdir(CSV_FOLDER) if f.endswith('.csv')]
    
    if not files:
        flash("No CSV file available to display.", "error")
        return redirect(url_for('upload_file'))
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(CSV_FOLDER, f)))
    csv_path = os.path.join(CSV_FOLDER, latest_file)
    
    df = pd.read_csv(csv_path, engine="python").fillna("")  # Replace NaN with empty strings
    total_rows = len(df)
    
    # Get current page number from request arguments, default to 1
    page = request.args.get('page', 1, type=int)
    
    # Calculate start and end row indices for pagination
    start_idx = (page - 1) * ROWS_PER_PAGE
    end_idx = start_idx + ROWS_PER_PAGE

    # Slice DataFrame for the current page
    df_paginated = df.iloc[start_idx:end_idx]

    # Convert DataFrame to HTML
    table_html = df_paginated.to_html(classes='table table-striped', index=False, escape=False)

    return render_template(
        'view_csv.html', 
        table=table_html, 
        title="CSV Preview", 
        page=page, 
        total_pages=ceil(total_rows / ROWS_PER_PAGE)
    )


@app.route('/api/data')
def get_data():
    """Serves the latest CSV data as JSON"""
    files = [f for f in os.listdir(CSV_FOLDER) if f.endswith('.csv')]
    
    if not files:
        return jsonify({"error": "No data available"}), 404
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(CSV_FOLDER, f)))
    csv_path = os.path.join(CSV_FOLDER, latest_file)
    
    df = pd.read_csv(csv_path).fillna(0)

    # Convert relevant columns to JSON
    data = {
        "latitude": df["latitude"].tolist(),
        "longitude": df["longitude"].tolist(),
        "battery": df["percentageCapacity"].tolist(),
        "altitude": df["altitude"].tolist(),
        "velN": df["velN"].tolist(),
        "velE": df["velE"].tolist(),
        "velD": df["velD"].tolist(),
        "gyroX": df["gyroX"].tolist(),
        "gyroY": df["gyroY"].tolist(),
        "gyroZ": df["gyroZ"].tolist(),
        "gimbal_roll": df["Gimbal:roll"].tolist(),
        "gimbal_pitch": df["Gimbal:pitch"].tolist(),
        "gimbal_yaw": df["Gimbal:yaw"].tolist(),
        "current": df["current"].tolist(),
        "voltage": df[["volt1", "volt2", "volt3", "volt4", "volt5", "volt6"]].to_dict(orient='list'),
        "temperature": df["batteryTemp(C)"].tolist()
    }
    
    return jsonify(data)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
