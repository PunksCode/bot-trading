import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Para limpiar textos feos

print("----------- RESULTADO -----------")
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"✅ ¡ÉXITO TOTAL! Tu GPU está lista: {gpus[0].name}")
    print("Ya puedes entrenar modelos a máxima velocidad.")
else:
    print("❌ Aún no detecta la GPU (Pero no te preocupes, funcionará con CPU).")