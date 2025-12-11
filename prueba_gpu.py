import tensorflow as tf
import os

# Eliminamos logs molestos
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("----------- DIAGNÓSTICO DE GPU -----------")
print(f"Versión de TensorFlow: {tf.__version__}")

# Listar dispositivos físicos
gpus = tf.config.list_physical_devices('GPU')

if gpus:
    print(f"\n✅ ¡ÉXITO! GPU DETECTADA:")
    for gpu in gpus:
        print(f"  - {gpu.name} (Tipo: {gpu.device_type})")
    print("\nTu RTX 2060 está lista para entrenar redes neuronales.")
else:
    print("\n❌ ALERTA: No se detectó GPU.")
    print("TensorFlow usará la CPU (funcionará, pero será lento).")
    print("Posible solución: Actualiza los drivers de NVIDIA desde GeForce Experience.")
print("------------------------------------------")
