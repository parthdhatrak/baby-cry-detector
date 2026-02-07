# Baby Cry Reason Detection API

A production-ready Django application that uses deep learning to detect and classify baby cry reasons from audio files.

## 🎯 Features

- **Multi-class Classification**: Detects 5 cry reasons (hungry, belly_pain, burping, discomfort, tired)
- **REST API**: Secure API endpoint with API key authentication
- **Web Interface**: User-friendly upload form with real-time results
- **Production Ready**: Configured for Render.com deployment with Gunicorn

## 📁 Project Structure

```
crybaby/
├── crybaby/                    # Django project configuration
│   ├── __init__.py
│   ├── settings.py             # Settings with model & audio config
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py                 # WSGI for Gunicorn
│   └── asgi.py                 # ASGI support
├── crydetector/                # Main application
│   ├── __init__.py
│   ├── apps.py                 # App config (model loading at startup)
│   ├── model_loader.py         # Singleton model loader
│   ├── audio_utils.py          # Audio preprocessing (MFCC extraction)
│   ├── views.py                # API & template views
│   ├── urls.py                 # App URL routing
│   └── templates/
│       └── crydetector/
│           └── home.html       # Upload form & results page
├── models/                     # Place cry_model.h5 here
├── manage.py
├── requirements.txt
├── Procfile                    # Render/Heroku deployment
├── build.sh                    # Build script for Render
├── runtime.txt                 # Python version
├── .env.example                # Environment template
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Local Development

1. **Clone and setup virtual environment**
   ```bash
   cd crybaby
   python -m venv venv
   venv\Scripts\activate      # Windows
   # source venv/bin/activate # Linux/Mac
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

4. **Add your model**
   
   Place your trained `cry_model.h5` file in the `models/` directory.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web UI: http://localhost:8000/
   - API: http://localhost:8000/api/predict/
   - Health: http://localhost:8000/health/

## 📡 API Usage

### Endpoint: `POST /api/predict/`

**Headers:**
```
X-API-KEY: your-api-key
Content-Type: multipart/form-data
```

**Request Body:**
- `audio_file`: WAV audio file

**Success Response (200):**
```json
{
    "is_crying": true,
    "predicted_reason": "hungry",
    "confidence": 0.87
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing API key
- `400 Bad Request`: Invalid file format
- `500 Internal Error`: Processing failed

### Example with cURL

```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "X-API-KEY: your-api-key" \
  -F "audio_file=@/path/to/baby_cry.wav"
```

### Example with Python

```python
import requests

url = "http://localhost:8000/api/predict/"
headers = {"X-API-KEY": "your-api-key"}
files = {"audio_file": open("baby_cry.wav", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

## ☁️ Deployment to Render.com

### Step 1: Prepare Repository

1. Initialize git repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Push to GitHub/GitLab

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Web Service**
3. Connect your repository
4. Configure:
   - **Name**: crybaby
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn crybaby.wsgi`

### Step 3: Configure Environment Variables

Add these environment variables in Render:

| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | Generate a secure key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CRY_DETECTION_API_KEY` | Your API key |
| `PYTHON_VERSION` | `3.11.0` |

### Step 4: Upload Model

Option A: Include in repository (not recommended for large files)

Option B: Use Render Disk:
1. Add a disk in Render settings
2. Mount at `/opt/render/project/models`
3. Set `MODEL_PATH=/opt/render/project/models/cry_model.h5`

### Step 5: Deploy

Click **Deploy** and wait for build completion.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | dev key |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `CRY_DETECTION_API_KEY` | API authentication key | dev key |
| `MODEL_PATH` | Path to .h5 model file | `models/cry_model.h5` |

### Audio Configuration

Configured in `settings.py`:

```python
AUDIO_CONFIG = {
    'SAMPLE_RATE': 22050,    # Hz
    'N_MFCC': 40,            # MFCC coefficients
    'MAX_PAD_LEN': 174,      # Fixed time steps
}
```

## 📋 Model Requirements

Your `cry_model.h5` should:

- Accept input shape: `(batch_size, 40, 174, 1)` - (40 MFCCs × 174 time steps × 1 channel)
- Output: 5-class softmax probabilities
- Classes order: `['hungry', 'belly_pain', 'burping', 'discomfort', 'tired']`

## ⚠️ Notes

- The application works in **demo mode** if the model file is not found
- Audio files must be in WAV format
- Maximum file size: 10MB
- The model loads once at startup, not per request

## 📄 License

MIT License
