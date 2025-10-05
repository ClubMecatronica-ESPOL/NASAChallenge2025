import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from pyproj import Transformer
import os

# --- Importaciones de Machine Learning ---
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer 

# =================================================================
# === PARTE 1: PREPARACIÓN DEL DATAFRAME Y DEFINICIÓN DE OBJETIVOS ===
# =================================================================

# 1.1: DEFINICIÓN DE ARCHIVOS Y RUTAS (AJUSTA ESTAS RUTAS)
BASE_DIR = "data_challenge/tiburon/" # La carpeta donde están todos los CSV de tiburones

# ⚠️ LISTA DE TODOS LOS ARCHIVOS DE SEGUIMIENTO
shark_files = [
    "160424_2013_132346pnas_atn.csv",
    "160424_2014_141195pnas_atn.csv",# El que ya tenías
    "160424_2015_141261pnas_atn.csv",
    "160424_2015_141264pnas_atn.csv",
    "160424_2015_141268pnas_atn.csv",
    "160424_2015_141270pnas_atn.csv",
    "160424_2016_106744pnas_atn.csv",       
    "160424_2016_106745pnas_atn.csv",
    "160424_2016_106746pnas_atn.csv",
    "160424_2016_106747pnas_atn.csv",
    "160424_2016_106748pnas_atn.csv",
    "160424_2016_141262pnas_atn.csv",
    "160424_2016_141263pnas_atn.csv",
    "160424_2016_141265pnas_atn.csv",
    "160424_2016_141266pnas_atn.csv",
    "160424_2016_165927pnas_atn.csv",
    "160424_2016_165928pnas_atn.csv",
]

COMBINED_FILE_PATH = "datos_modelo.csv" 
final_trajectories = [] # Lista para almacenar el DataFrame interpolado de cada tiburón

# Bucle para procesar cada archivo de tiburón
for i, file_name in enumerate(shark_files):
    shark_id = f"TIBURON_{i+1}"
    shark_file_path = os.path.join(BASE_DIR, file_name)

    try:
        df = pd.read_csv(shark_file_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        def parse_depth(x):
            try:
                return int(x)
            except:
                return np.nan
        df["depth"] = df["lc"].apply(parse_depth)
        
        # Proyección e Interpolación (sin cambios)
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        df["x"], df["y"] = transformer.transform(df["lon"].values, df["lat"].values)
        df["t_s"] = (df["date"] - df["date"].iloc[0]).dt.total_seconds()
        uniq = df.drop_duplicates(subset="t_s")
        t = uniq["t_s"].values
        depth_filled = uniq["depth"].ffill().bfill()
        fx = interp1d(t, uniq["x"], kind="linear", fill_value="extrapolate")
        fy = interp1d(t, uniq["y"], kind="linear", fill_value="extrapolate")
        fz = interp1d(t, depth_filled, kind="nearest", fill_value="extrapolate")
        step = 6 * 3600
        t_new = np.arange(t.min(), t.max(), step)
        x_new, y_new, z_new = fx(t_new), fy(t_new), fz(t_new)
        lon_new, lat_new = transformer.transform(x_new, y_new, direction="INVERSE")

        df_traj = pd.DataFrame({
            't_s': t_new,
            'lon': lon_new,
            'lat': lat_new,
            'Profundidad': np.clip(np.round(z_new).astype(int), 0, 3),
            'id_tiburon': shark_id # 🔑 IMPORTANTE: Asignar ID único
        })
        # Asignar el año de la primera entrada (asumiendo que el seguimiento es en un solo año)
        df_traj['year'] = df["date"].iloc[0].year 
        
        final_trajectories.append(df_traj)

    except FileNotFoundError:
        print(f"ADVERTENCIA: Archivo de tiburón {shark_id} ({file_name}) no encontrado. Saltando.")
    except Exception as e:
        print(f"ERROR procesando tiburón {shark_id}: {e}. Saltando.")

# 1.2: Concatenar todos los DataFrames de trayectorias
if not final_trajectories:
    print("ERROR FATAL: No se pudo cargar ningún archivo de tiburón. Terminando.")
    exit()
    
df_traj_all = pd.concat(final_trajectories, ignore_index=True)
print(f"--- Trayectorias de {len(final_trajectories)} tiburones cargadas. Total de puntos: {len(df_traj_all)} ---")


# =================================================================
# === CARGA DE DATOS AMBIENTALES Y UNIÓN (MERGE) ===
# =================================================================

try:
    df_combined = pd.read_csv(COMBINED_FILE_PATH, na_values=['NaN', 'NULL', ''])
    
    # CORRECCIÓN DE ETIQUETAS
    df_combined = df_combined.rename(columns={
        'latitude': 'lat',                
        'longitude': 'lon',               
        'concentracion_clorofila': 'Cloro_Media', 
        'temperatura': 'Temp_Media',      
        'year': 'year'                    
    })
    
    # CLAVE PARA LA UNIÓN: Redondeo de coordenadas
    DECIMAL_PRECISION = 2 
    df_combined['lat'] = df_combined['lat'].round(DECIMAL_PRECISION)
    df_combined['lon'] = df_combined['lon'].round(DECIMAL_PRECISION)
    
    # Crear claves redondeadas en los datos de la trayectoria
    df_traj_all['lat_key'] = df_traj_all['lat'].round(DECIMAL_PRECISION)
    df_traj_all['lon_key'] = df_traj_all['lon'].round(DECIMAL_PRECISION)

    # A. Unir la trayectoria del tiburón con los datos ambientales
    df_ml = pd.merge(
        df_traj_all, # Usamos el DataFrame concatenado
        df_combined[['lat', 'lon', 'year', 'Temp_Media', 'Cloro_Media']],
        left_on=['lat_key', 'lon_key', 'year'],
        right_on=['lat', 'lon', 'year'],
        how='left',
        suffixes=('_traj', '_env')
    )
    
    # Limpieza
    df_ml.drop(columns=['lat_key', 'lon_key', 'lat_env', 'lon_env'], inplace=True)
    df_ml.rename(columns={'lat_traj': 'lat', 'lon_traj': 'lon'}, inplace=True)
    
    print("--- Datos Ambientales unidos exitosamente a las trayectorias combinadas ---")
    
except FileNotFoundError:
    print(f"ERROR: Archivo CSV Combinado no encontrado. Usando NaN para ambientales en todos los tiburones.")
    df_ml = df_traj_all.copy()
    df_ml['Temp_Media'] = np.nan
    df_ml['Cloro_Media'] = np.nan
    
except Exception as e:
    print(f"ERROR al procesar el archivo CSV combinado durante la unión: {e}. Asignando NaN.")
    df_ml = df_traj_all.copy()
    df_ml['Temp_Media'] = np.nan
    df_ml['Cloro_Media'] = np.nan
    
    
# B. CREAR OBJETIVOS (NUEVA POSICIÓN)
df_ml['lon_futura'] = df_ml.groupby('id_tiburon')['lon'].shift(-1) # <<-- SHIFT POR GRUPO
df_ml['lat_futura'] = df_ml.groupby('id_tiburon')['lat'].shift(-1) # <<-- SHIFT POR GRUPO

# C. Limpieza: Solo eliminamos filas donde falta el OBJETIVO (lon/lat futuras)
# Esto garantiza que el último punto de CADA tiburón se elimine correctamente.
df_ml.dropna(subset=['lon_futura', 'lat_futura'], inplace=True)

print(f"\nTotal de puntos para entrenar de todos los tiburones: {len(df_ml)}")

# =================================================================
# === PARTE 2: CREACIÓN DEL PIPELINE Y MODELADO (REGRESIÓN LINEAL) ===
# =================================================================

# 2.1: Definición de Features y Target
features = ['lon', 'lat', 'Temp_Media', 'Cloro_Media']
targets = ['lon_futura', 'lat_futura']

X = df_ml[features]
Y = df_ml[targets]

# Nota: Mantener shuffle=False y random_state=42 para reproducibilidad
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, shuffle=False, random_state=42)

# 2.2: Preprocesamiento con ColumnTransformer
features_num = ['lon', 'lat', 'Temp_Media', 'Cloro_Media']

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')), 
    ('scaler', StandardScaler())
])

# El ColumnTransformer ahora solo procesa las features numéricas
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, features_num), 
    ],
    remainder='drop' # Elimina las columnas que no están en features_num (como Profundidad e id_tiburon)
)

# 2.3: Creación del Pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', MultiOutputRegressor(LinearRegression()))
])

print("\n--- Pipeline Configurado para Múltiples Tiburones (Regresión Lineal) ---")

# =================================================================
# === PARTE 3: ENTRENAMIENTO, PREDICCIÓN Y EVALUACIÓN ===
# =================================================================

print("\n--- Iniciando Entrenamiento del Modelo ---")
model_pipeline.fit(X_train, Y_train)
print("--- Entrenamiento Completo ---")

# Predicción de la NUEVA POSICIÓN
pos_pred = model_pipeline.predict(X_test)
pos_pred = pd.DataFrame(pos_pred, columns=targets, index=Y_test.index)

# 3.1: Medición de Métricas
rmse_lon = np.sqrt(mean_squared_error(Y_test['lon_futura'], pos_pred['lon_futura']))
r2_lon = r2_score(Y_test['lon_futura'], pos_pred['lon_futura'])
rmse_lat = np.sqrt(mean_squared_error(Y_test['lat_futura'], pos_pred['lat_futura']))
r2_lat = r2_score(Y_test['lat_futura'], pos_pred['lat_futura'])

print("\n--- Evaluación de Métricas de Precisión (Múltiples Tiburones) ---")
print(r"Predicción de Longitud Futura ($\text{lon}_{futura}$):")
print(f"  RMSE (Error de Posición): {rmse_lon:.4f} grados")
print(f"  R² (Varianza Explicada): {r2_lon:.4f}")

print(r"\nPredicción de Latitud Futura ($\text{lat}_{futura}$):")
print(f"  RMSE (Error de Posición): {rmse_lat:.4f} grados")
print(f"  R² (Varianza Explicada): {r2_lat:.4f}")

import joblib
import os

# Define la ruta para guardar el pipeline entrenado
# La extensión .pkl (pickle) o .joblib es estándar
MODEL_FILENAME = 'modelo_trayectoria_lineal.joblib'

# Guardar el pipeline completo (preprocesador + modelo)
try:
    joblib.dump(model_pipeline, MODEL_FILENAME)
    print(f"\n✅ Modelo y Pipeline guardados exitosamente como {MODEL_FILENAME}")
except Exception as e:
    print(f"\n❌ ERROR al guardar el modelo: {e}")