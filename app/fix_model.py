import tensorflow as tf
from tensorflow.keras.saving import custom_object_scope

# Path to your old model
old_model_path = "models/plant_disease_model.h5"

# Path for new fixed model
new_model_path = "models/plant_disease_model.keras"

print("Loading old model...")

# Fix TrueDivide issue while loading
with custom_object_scope({'TrueDivide': tf.math.truediv}):
    model = tf.keras.models.load_model(old_model_path, compile=False)

print("Model loaded successfully!")

# Save in new format (best format)
model.save(new_model_path)

print("✅ Model converted and saved as .keras format!")