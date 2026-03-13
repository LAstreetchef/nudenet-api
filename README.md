# NudeNet API

Simple Flask API for NSFW content detection using NudeNet.

## Endpoints

### `GET /health`
Health check endpoint.

### `POST /detect`
Detect NSFW content in an image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `image` file field

**Response:**
```json
{
  "isNSFW": true,
  "detections": [
    {
      "label": "FEMALE_BREAST_EXPOSED",
      "confidence": 0.95,
      "box": [x, y, width, height]
    }
  ],
  "reason": "Detected FEMALE_BREAST_EXPOSED (95% confidence)"
}
```

## Deployment

Deploys automatically to Render via `render.yaml`.

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

The API will run on port 5001 by default.
