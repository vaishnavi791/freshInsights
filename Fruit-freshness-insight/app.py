# app.py
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

# app.py - CORRECTED VERSION
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

# ✅ FIXED: Alphabetical order to match folder scanning
RIPENESS_CLASSES = ['Overripe', 'Ripe', 'Unripe', 'Not Fruit']
#                    0          1       2         3
FRUIT_TYPES = ['Apple', 'Orange']

def load_model():
    model_path = 'fruit_ripeness_with_person_rejection.keras'
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
    
    # ✅ DEBUG: Print raw probabilities
    print("\n" + "="*50)
    print("🔍 RAW MODEL PREDICTIONS:")
    print("="*50)
    for i, cls in enumerate(RIPENESS_CLASSES):
        print(f"  {cls:12} -> {ripeness_probs[i]:.4f} ({ripeness_probs[i]*100:.2f}%)")
    print("\nFruit Type Predictions:")
    for i, cls in enumerate(FRUIT_TYPES):
        print(f"  {cls:12} -> {fruit_probs[i]:.4f} ({fruit_probs[i]*100:.2f}%)")
    print("="*50 + "\n")
    
    ripeness_idx = int(np.argmax(ripeness_probs))
    fruit_idx = int(np.argmax(fruit_probs))
    
    ripeness = RIPENESS_CLASSES[ripeness_idx]
    ripeness_conf = float(ripeness_probs[ripeness_idx])
    
    # ✅ DEBUG: Print final decision
    print(f"✅ FINAL DECISION: {FRUIT_TYPES[fruit_idx]} - {ripeness}")
    
    # Check if "Not Fruit" detected
    if ripeness_idx == 3:  # Not Fruit
        return {
            'is_fruit': False,
            'ripeness': ripeness,
            'ripeness_conf': ripeness_conf,
            'fruit': 'N/A',
            'fruit_conf': 0.0,
            'ripeness_probs': ripeness_probs.tolist(),
            'fruit_probs': fruit_probs.tolist()
        }
    else:
        return {
            'is_fruit': True,
            'ripeness': RIPENESS_CLASSES[ripeness_idx],
            'ripeness_conf': ripeness_conf,
            'fruit': FRUIT_TYPES[fruit_idx],
            'fruit_conf': float(fruit_probs[fruit_idx]),
            'ripeness_probs': ripeness_probs.tolist(),
            'fruit_probs': fruit_probs.tolist()
        }


