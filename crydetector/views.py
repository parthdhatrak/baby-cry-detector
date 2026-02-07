import logging
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .audio_utils import preprocess_audio, validate_audio_file
from .model_loader import is_model_available, predict_fast

logger = logging.getLogger(__name__)

def verify_api_key(request):
    import hmac
    key = request.headers.get('X-API-KEY', '')
    return hmac.compare_digest(key, settings.API_KEY)

def home_view(request):
    context = {'result': None, 'error': None, 'model_available': is_model_available()}
    if request.method == 'POST':
        file = request.FILES.get('audio_file')
        valid, err = validate_audio_file(file)
        if not valid:
            context['error'] = err
        else:
            try:
                context['result'] = process_prediction(file)
            except Exception as e:
                context['error'] = str(e)
    return render(request, 'crydetector/home.html', context)

@csrf_exempt
def api_v1_predict(request):
    """
    CLEAN REST API: POST /api/v1/predict/
    Accepts: multipart/form-data with 'audio' field
    Security: X-API-KEY header
    """
    # 1. Method Validation
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # 2. Security: API Key validation
    if not verify_api_key(request):
        return JsonResponse({'error': 'Invalid or missing API key'}, status=401)

    # 3. Input Validation
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'Missing audio file in field "audio"'}, status=400)

    # 4. Content-Type / Extension Check
    if not audio_file.name.lower().endswith('.wav'):
        return JsonResponse({'error': 'Unsupported file type. Only .wav is accepted'}, status=415)

    try:
        # 5. Preprocessing (Extracted features)
        features = preprocess_audio(audio_file)
        
        # 6. Inference
        probs = predict_fast(features)
        
        # 7. Success Response
        classes = settings.CRY_CLASSES
        idx = np.argmax(probs)
        
        return JsonResponse({
            'label': classes[idx],
            'confidence': round(float(probs[idx]), 4),
            'reason': settings.CRY_REASONS.get(classes[idx], "No specific reason identified."),
            'probabilities': {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
        })

    except ValueError as e:
        # preprocess_audio raises ValueError for processing failures (corrupted/silent)
        return JsonResponse({'error': f'Corrupted or silent audio: {str(e)}'}, status=422)
    except Exception as e:
        logger.error(f"API Prediction error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def process_prediction(audio_file):
    """
    Consolidated prediction path optimized for latency.
    """
    # 1. Preprocess
    features = preprocess_audio(audio_file)
    
    # 2. Inference (Fast Path)
    probs = predict_fast(features)
    
    # 3. Post-process
    classes = settings.CRY_CLASSES
    reasons = settings.CRY_REASONS
    idx = np.argmax(probs)
    confidence = float(probs[idx])
    label = classes[idx]
    
    return {
        'is_crying': confidence > 0.4,
        'predicted_label': label,
        'confidence': round(confidence, 4),
        'reason': reasons.get(label, "No specific reason identified."),
        'probabilities': {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
    }

def health_check(request):
    return JsonResponse({'status': 'ok', 'model_ready': is_model_available()})
