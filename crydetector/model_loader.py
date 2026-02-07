import os
import logging
import tensorflow as tf
from django.conf import settings

# Speed Optimization: Disable unnecessary TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logger = logging.getLogger(__name__)

_model = None

def get_model():
    """
    Singleton loader with warm-up logic to eliminate latency.
    """
    global _model
    if _model is None:
        try:
            logger.info("Loading model for the first time...")
            _model = tf.keras.models.load_model(settings.MODEL_PATH, compile=False)
            
            # Warm-up call: forces TF to initialize graph/kernels
            # Prevents 1-2s delay on the first real prediction
            logger.info("Warming up model...")
            dummy = tf.zeros((1, 40, 173, 1))
            _model(dummy, training=False)
            logger.info("Model ready.")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return None
    return _model

def predict_fast(features):
    """
    High-speed inference using direct __call__.
    Faster than .predict() for single samples.
    """
    model = get_model()
    if model is None: raise RuntimeError("Model unavailable")
    
    # Input conversion
    tensor_input = tf.convert_to_tensor(features)
    
    # Single sample inference is faster via direct call
    logits = model(tensor_input, training=False)
    
    return logits.numpy()[0]

def is_model_available():
    return get_model() is not None
