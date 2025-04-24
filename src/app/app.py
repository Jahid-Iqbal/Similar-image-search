from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import os
import sys
from pathlib import Path
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path configuration
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

app = Flask(__name__,
            template_folder=str(project_root / 'templates'),
            static_folder=str(project_root / 'static'))

# External image folder (fixed location, not within static)
EXTERNAL_IMAGE_FOLDER = r'E:\Projects\Image search_V2\images'

# Configuration
app.config.update({
    'UPLOAD_FOLDER': str(project_root / 'static' / 'uploads'),
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'webp'},
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'STATIC_CACHE_CONTROL': 'max-age=604800'  # 1 week cache
})

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Secure filename and save
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Perform search
        from scripts.search_images import search_similar_images
        results = search_similar_images(save_path)

        # Prepare results with web paths
        valid_results = []
        for hit in results:
            full_image_path = hit["_source"]["image_path"]  # Full or relative file path
            basename = os.path.basename(full_image_path)
            image_file_path = os.path.join(EXTERNAL_IMAGE_FOLDER, basename)

            if os.path.exists(image_file_path):
                valid_results.append({
                    "path": f"/external-images/{basename}",  # ✅ Web-accessible path
                    "score": round(hit["_score"], 4)
                })
            else:
                logger.warning(f"Missing image: {image_file_path}")

        return jsonify({
            "query_image": f"/static/uploads/{filename}",
            "results": valid_results
        })

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({"error": "Search failed"}), 500

@app.route('/external-images/<filename>')
def serve_external_image(filename):
    file_path = os.path.join(EXTERNAL_IMAGE_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        logger.warning(f"Requested image not found: {file_path}")
        return jsonify({"error": "Image not found"}), 404

@app.route('/static/<path:path>')
def serve_static(path):
    response = send_from_directory(app.static_folder, path)
    response.headers['Cache-Control'] = app.config['STATIC_CACHE_CONTROL']
    return response

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
