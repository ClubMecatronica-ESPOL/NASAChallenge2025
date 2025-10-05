import pandas as pd
import joblib
import numpy as np

# --- Replicar la preparación de datos mínima (solo la necesaria para las FEATURES) ---
# Importa solo las herramientas que necesitas para cargar y preparar los nuevos datos.
# Por simplicidad, se omite la lógica de interpolación/proyección aquí, asumiendo que 
# los nuevos datos ya están en el formato de df_ml (lon, lat, Profundidad, Temp_Media, Cloro_Media, id_tiburon)
# Si tus nuevos datos no están en ese formato, debes incluir la lógica de preprocesamiento de la Parte 1.

# Nombre del archivo del modelo guardado
MODEL_FILENAME = 'modelo_trayectoria_lineal.joblib'

# --- 1. Cargar el Modelo ---
try:
    modelo_cargado = joblib.load(MODEL_FILENAME)
    print(f"✅ Modelo {MODEL_FILENAME} cargado.")
except FileNotFoundError:
    print(f"❌ ERROR: El archivo del modelo {MODEL_FILENAME} no se encuentra.")
    exit()

# --- 2. Preparar los Nuevos Datos de Predicción (Ejemplo Simulado) ---

# Supongamos que tienes un nuevo tiburón (TIBURON_12) en esta posición y condiciones.
# El modelo SOLO necesita las FEATURES que usaste para entrenar.
nuevos_datos = pd.DataFrame({
    'lon': [-71.5], 
    'lat': [41.2],
    'Profundidad': [2],
    'Temp_Media': [15.5],  # O el valor imputado si no hay match ambiental
    'Cloro_Media': [0.5], # O el valor imputado si no hay match ambiental
    'id_tiburon': ['TIBURON_12']
})

# NOTA IMPORTANTE: Si la columna 'id_tiburon' es nueva (ej. 'TIBURON_12'), 
# el OneHotEncoder lo ignorará automáticamente gracias a 'handle_unknown="ignore"', 
# y usará la predicción promedio de la población entrenada.

# Asegúrate de que las columnas estén en el orden correcto si tu modelo lo requiere
FEATURES = ['lon', 'lat', 'Temp_Media', 'Cloro_Media']
X_new = nuevos_datos[FEATURES]

# --- 3. Predecir ---
print("\n--- Iniciando Predicción ---")
# El pipeline cargado automáticamente aplica la imputación y la estandarización.
predicciones = modelo_cargado.predict(X_new)

# --- 4. Mostrar Resultados ---
lon_futura_pred = predicciones[0][0]
lat_futura_pred = predicciones[0][1]

print("\n--- Resultados de la Predicción (Siguiente Posición) ---")
print(f"Posición Actual: Longitud {nuevos_datos['lon'].iloc[0]:.4f}, Latitud {nuevos_datos['lat'].iloc[0]:.4f}")
print(f"Posición Predicha: Longitud {lon_futura_pred:.4f}, Latitud {lat_futura_pred:.4f}")