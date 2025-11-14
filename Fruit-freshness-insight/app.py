# app.py
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

RIPENESS_CLASSES = ['Unripe', 'Ripe', 'Overripe']
FRUIT_TYPES = ['Apple', 'Orange']

def load_model():
    model_path = 'fruit_ripeness_multitask_finetuned.keras'
    return tf.keras.models.load_model(model_path)

model = load_model()

def preprocess_image(image_pil):
    img = np.array(image_pil)
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    img = cv2.resize(img, (224, 224))
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img.astype('float32'))
    img = np.expand_dims(img, axis=0)
    return img

def get_prediction(image_pil):
    processed = preprocess_image(image_pil)
    predictions = model.predict(processed, verbose=0)
    ripeness_probs = predictions[0][0]
    fruit_probs = predictions[1][0]
    
    ripeness_idx = int(np.argmax(ripeness_probs))
    fruit_idx = int(np.argmax(fruit_probs))
    
    return {
        'ripeness': RIPENESS_CLASSES[ripeness_idx],
        'ripeness_conf': float(ripeness_probs[ripeness_idx]),
        'fruit': FRUIT_TYPES[fruit_idx],
        'fruit_conf': float(fruit_probs[fruit_idx])
    }