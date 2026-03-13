from flask import Flask, request, jsonify
from nudenet import NudeDetector
import tempfile
import os

app = Flask(__name__)

# Initialize the detector (loads model on startup)
print("[NudeNet] Loading model...")
detector = NudeDetector()
print("[NudeNet] Model loaded successfully")

# NSFW labels from NudeNet
NSFW_LABELS = {
    'FEMALE_GENITALIA_EXPOSED',
    'FEMALE_BREAST_EXPOSED', 
    'MALE_GENITALIA_EXPOSED',
    'ANUS_EXPOSED',
    'BUTTOCKS_EXPOSED'
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'loaded'})

@app.route('/detect', methods=['POST'])
def detect():
    """
    Detect NSFW content in an uploaded image
    
    Expects: multipart/form-data with 'image' file
    Returns: JSON with isNSFW boolean and detections array
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        image_file.save(tmp.name)
        temp_path = tmp.name
    
    try:
        # Run detection
        detections = detector.detect(temp_path)
        
        # Check for NSFW content
        nsfw_found = any(
            det['class'] in NSFW_LABELS and det['score'] > 0.6
            for det in detections
        )
        
        # Filter to only NSFW detections above threshold
        nsfw_detections = [
            {
                'label': det['class'],
                'confidence': round(det['score'], 3),
                'box': det['box']
            }
            for det in detections
            if det['class'] in NSFW_LABELS and det['score'] > 0.6
        ]
        
        result = {
            'isNSFW': nsfw_found,
            'detections': nsfw_detections,
            'total_detections': len(detections)
        }
        
        if nsfw_found:
            highest = max(nsfw_detections, key=lambda x: x['confidence'])
            result['reason'] = f"Detected {highest['label']} ({int(highest['confidence'] * 100)}% confidence)"
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
