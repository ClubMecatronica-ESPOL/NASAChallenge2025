import pandas as pd
import numpy as np # Necesario para usar np.nan

# --- Nombres de tus archivos (AJUSTA ESTOS NOMBRES) ---
archivo_clorofila = "C:/Users/User/Downloads/NASA/clorofila_2013_2017.csv"
archivo_temperatura = "C:/Users/User/Downloads/NASA/temperatura_superficial_2013_2017.csv"
archivo_salida = 'datos_modelo.csv'
# --------------------------------------------------------

# 1. Cargar los datasets
try:
    df_clorofila = pd.read_csv(archivo_clorofila)
    df_temperatura = pd.read_csv(archivo_temperatura)
except FileNotFoundError as e:
    print(f"Error: No se pudo encontrar el archivo. Asegúrate de que los nombres son correctos y el archivo está en la ubicación esperada. Detalle: {e}")
    exit()

# 2. Renombrar las columnas para que Pandas sepa cómo unirlas
# Supongo que las columnas del primer archivo son: lat, lon, clorofila, año
# Y las del segundo son: lat, lon, temperatura, año

# Aseguramos que los nombres de las columnas que queremos unir sean idénticos
columnas_clave = ['latitude', 'longitude', 'year']
# Renombramos las columnas del valor de interés si tienen un nombre diferente
df_clorofila = df_clorofila.rename(columns={'clorofila': 'concentracion_clorofila'})
df_temperatura = df_temperatura.rename(columns={'temperatura': 'temperatura'})
# NOTA: Ajusta 'clorofila' y 'temperatura' en las líneas anteriores si en tus CSV tienen otros nombres.

# 3. Combinar los datasets
# Usaremos pd.merge() con un método 'outer' (unión externa)
# Esto asegura que MANTENEMOS TODAS las filas de AMBOS archivos.
# Si una combinación (lat, lon, año) existe en uno pero no en el otro,
# el valor de la columna faltante se rellenará automáticamente con NaN.

df_combinado = pd.merge(
    df_clorofila,
    df_temperatura,
    on=columnas_clave, # Columnas comunes para la unión
    how='outer'        # 'outer' es clave: mantiene todas las filas y usa NaN para faltantes
)

# 4. (Opcional) Ver un resumen de los datos combinados
print("Primeras 5 filas del archivo combinado:")
print(df_combinado.head())

print("\nConteo de valores NaN (datos faltantes) por columna:")
print(df_combinado.isnull().sum())

# 5. Guardar el nuevo archivo CSV
# Pandas escribe NaN como una cadena vacía en el CSV por defecto,
# pero si quieres una representación más explícita (como 'NaN' o 'Null') en el archivo,
# puedes usar el parámetro 'na_rep'. Para modelos, la representación por defecto de Pandas (NaN) está bien.

# Para asegurar la representación de 'NaN' en el archivo, que es lo que quieres:
df_combinado.to_csv(archivo_salida, index=False, na_rep='NaN') 
# na_rep='NaN' asegura que el texto "NaN" aparece en el CSV donde falta un dato.
# index=False evita guardar la columna de índice de Pandas.

print(f"\n✅ Proceso completado. Archivo combinado guardado como: {archivo_salida}")
print("El archivo resultante contiene las columnas:", df_combinado.columns.tolist())