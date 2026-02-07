import os
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SR = 22050
DURATION = 4
N_MFCC = 40
N_FFT = 2048
HOP_LENGTH = 512
MAX_PAD_LEN = 173
DATA_DIR = 'donateacry_corpus_cleaned_and_updated_data'
CLASSES = ['belly_pain', 'burping', 'discomfort', 'hungry', 'tired']

def extract_features(file_path, augment=False):
    try:
        y, sr = librosa.load(file_path, sr=SR, mono=True)
        if augment:
            if np.random.random() > 0.5:
                y = y + 0.002 * np.random.randn(len(y))
            if np.random.random() > 0.5:
                y = librosa.effects.time_stretch(y, rate=np.random.uniform(0.8, 1.2))
        
        target_samples = SR * DURATION
        if len(y) < target_samples:
            y = np.pad(y, (0, target_samples - len(y)))
        else:
            y = y[:target_samples]
            
        mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=N_MFCC, n_fft=N_FFT, hop_length=HOP_LENGTH)
        
        if mfcc.shape[1] < MAX_PAD_LEN:
            mfcc = np.pad(mfcc, ((0, 0), (0, MAX_PAD_LEN - mfcc.shape[1])))
        else:
            mfcc = mfcc[:, :MAX_PAD_LEN]
            
        mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)
        return mfcc
    except Exception:
        return None

def load_data_balanced():
    X = []
    y = []
    
    # We will aim for exactly 150 samples per class
    SAMPLES_PER_CLASS = 150
    
    for idx, label in enumerate(CLASSES):
        class_dir = os.path.join(DATA_DIR, label)
        files = [os.path.join(class_dir, f) for f in os.listdir(class_dir) if f.endswith('.wav')]
        
        # If hungry, take a random subset of 150
        if len(files) > SAMPLES_PER_CLASS:
            selected_files = np.random.choice(files, SAMPLES_PER_CLASS, replace=False)
        else:
            selected_files = files
            
        logger.info(f"Loading {label}...")
        for f in selected_files:
            feat = extract_features(f, augment=False)
            if feat is not None:
                X.append(feat)
                y.append(idx)
        
        # Fill up to 150 with augmented versions
        current_count = len([label_idx for label_idx in y if label_idx == idx])
        if current_count < SAMPLES_PER_CLASS:
            num_needed = SAMPLES_PER_CLASS - current_count
            logger.info(f"  Augmenting {label} to reach {SAMPLES_PER_CLASS}...")
            for _ in range(num_needed):
                f = np.random.choice(files)
                feat = extract_features(f, augment=True)
                if feat is not None:
                    X.append(feat)
                    y.append(idx)
                    
    X = np.array(X)
    y = np.array(y)
    X = X.reshape(X.shape[0], N_MFCC, MAX_PAD_LEN, 1)
    return X, y

def build_model():
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=(N_MFCC, MAX_PAD_LEN, 1)),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        
        layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        
        layers.Conv2D(128, (3, 3), padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(len(CLASSES), activation='softmax')
    ])
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model

if __name__ == "__main__":
    X, y = load_data_balanced()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    model = build_model()
    model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))
    model.save('baby_cry_reason_model.keras')
    logger.info("Retrained balanced model saved.")
