# app.py - FINAL ROBUST VERSION
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

RIPENESS_CLASSES = ['Unripe', 'Ripe', 'Overripe', 'Not Fruit']
FRUIT_TYPES = ['Apple', 'Orange']

def load_model():
    model_path = 'fruit_ripeness_with_person_rejection_IMPROVED.keras'
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
    
    # ✅ CONSERVATIVE BOOST: Only 15% (was 40%)
    OVERRIPE_BOOST = 1.15
    adjusted_probs = ripeness_probs.copy()
    adjusted_probs[2] *= OVERRIPE_BOOST
    adjusted_probs /= adjusted_probs.sum()
    
    ripeness_idx = int(np.argmax(adjusted_probs))
    fruit_idx = int(np.argmax(fruit_probs))
    
    ripeness = RIPENESS_CLASSES[ripeness_idx]
    ripeness_conf = float(adjusted_probs[ripeness_idx])
    
    # ✅ ONLY override if model is VERY confident about overripe
    # AND the confidence gap is significant
    if ripeness_idx == 2:  # Model says Overripe
        # Check if model is confident (>90%)
        if ripeness_conf > 0.90:
            print(f"✅ High confidence overripe: {ripeness_conf*100:.1f}%")
        else:
            # Check the margin between Overripe and Ripe
            ripe_prob = adjusted_probs[1]
            overripe_prob = adjusted_probs[2]
            margin = overripe_prob - ripe_prob
            
            print(f"🔍 Borderline case:")
            print(f"   Ripe: {ripe_prob*100:.1f}%")
            print(f"   Overripe: {overripe_prob*100:.1f}%")
            print(f"   Margin: {margin*100:.1f}%")
            
            # ✅ If margin is small (<15%), trust the model's original prediction
            # This avoids forcing overripe on borderline cases
            if margin < 0.15:
                # Use ORIGINAL probabilities (without boost)
                orig_ripeness_idx = int(np.argmax(ripeness_probs))
                if orig_ripeness_idx == 1:  # Original was Ripe
                    ripeness = 'Ripe'
                    ripeness_conf = float(ripeness_probs[1])
                    print(f"   ↩️ Reverting to Ripe (small margin)")
    
    if ripeness_idx == 3:
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
            'ripeness': ripeness,
            'ripeness_conf': ripeness_conf,
            'fruit': FRUIT_TYPES[fruit_idx],
            'fruit_conf': float(fruit_probs[fruit_idx]),
            'ripeness_probs': ripeness_probs.tolist(),
            'fruit_probs': fruit_probs.tolist()
        }
