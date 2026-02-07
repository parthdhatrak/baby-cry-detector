import io
import logging
import numpy as np
import librosa
from django.conf import settings

logger = logging.getLogger(__name__)

def validate_audio_file(file):
    """
    Validate the uploaded audio file.
    """
    if file is None:
        return False, "No file uploaded"
    
    filename = file.name.lower()
    if not filename.endswith('.wav'):
        return False, "Invalid format. Only .wav files are accepted"
    
    if file.size == 0:
        return False, "File is empty"
        
    return True, None

def preprocess_audio(file):
    """
    MATCHING TRAINING PREPROCESSING:
    1. Load at 22050 Hz
    2. Fixed 4s duration (padded or trimmed)
    3. MFCC (40 coefficients)
    4. NO additional scaling (model expects raw MFCC values)
    """
    try:
        # Load configuration
        sr = settings.AUDIO_CONFIG['SAMPLE_RATE']
        duration = settings.AUDIO_CONFIG['DURATION']
        n_mfcc = settings.AUDIO_CONFIG['N_MFCC']
        n_fft = settings.AUDIO_CONFIG['N_FFT']
        hop_l = settings.AUDIO_CONFIG['HOP_LENGTH']
        max_len = settings.AUDIO_CONFIG['MAX_PAD_LEN']
        
        # 1. Fast Memory Load
        audio_data = file.read()
        file.seek(0)
        y, _ = librosa.load(io.BytesIO(audio_data), sr=sr, mono=True)
        
        # 2. Match exact duration (Trimming silence first can help but 
        # let's stick to simple padding/trimming to match verify_alpha results)
        target_samples = int(sr * duration)
        if len(y) < target_samples:
            # Pad with zeros
            y = np.pad(y, (0, target_samples - len(y)))
        else:
            # Trim
            y = y[:target_samples]
            
        # 3. Feature Extraction
        # NOTE: librosa.feature.mfcc internally handles power_to_db scaling 
        # based on the melspectrogram it generates.
        mfcc = librosa.feature.mfcc(
            y=y, 
            sr=sr, 
            n_mfcc=n_mfcc, 
            n_fft=n_fft, 
            hop_length=hop_l
        )
        
        # 4. Ensure exact time-step shape for CNN
        if mfcc.shape[1] < max_len:
            mfcc = np.pad(mfcc, ((0, 0), (0, max_len - mfcc.shape[1])))
        else:
            mfcc = mfcc[:, :max_len]
            
        # 5. NORMALIZATION (Z-score)
        # Match training: mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)
        mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)
        
        # Reshape for CNN: (batch, n_mfcc, time_steps, channels)
        return mfcc.reshape(1, n_mfcc, max_len, 1).astype(np.float32)
        
    except Exception as e:
        logger.error(f"Audio preprocessing failed: {str(e)}")
        raise ValueError(f"Failed to process audio: {str(e)}")
