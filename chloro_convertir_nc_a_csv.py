import xarray as xr
import pandas as pd
import os
import re

# === CONFIGURACIÓN ===
carpeta = r"C:\Users\TuUsuario\Desktop\nasa\TuCarpetaConLosDatos"  # Cambia esta ruta a tu carpeta de archivos .nc
archivo_salida = "concentracion_clorofila.csv"
variable_objetivo = "chlor_a"  # Variable de clorofila

def extraer_año(nombre_archivo):
    """Detecta el año a partir del nombre del archivo."""
    match = re.search(r"20\d{2}", nombre_archivo)
    return int(match.group()) if match else None

# === PROCESAMIENTO ===
datos_combinados = []

for archivo in os.listdir(carpeta):
    if archivo.endswith(".nc"):
        ruta = os.path.join(carpeta, archivo)
        print(f"\nProcesando: {archivo}")
        ds = xr.open_dataset(ruta)

        if variable_objetivo not in ds.data_vars:
            print(f"⚠️ Variable '{variable_objetivo}' no encontrada, usando la primera variable numérica.")
            variable = list(ds.data_vars.keys())[0]
        else:
            variable = variable_objetivo

        da = ds[variable]

        # Manejar valores nulos o de relleno (_FillValue)
        fill = da.attrs.get("_FillValue", None)
        if fill is not None:
            da = da.where(da != fill)

        # Convertir a DataFrame
        df = da.to_dataframe().reset_index()
        df["year"] = extraer_año(archivo)

        # Renombrar columnas
        df = df.rename(columns={
            "lat": "latitude",
            "lon": "longitude",
            variable: "chlorophyll"
        })

        # Filtrar datos válidos
        df = df.dropna(subset=["chlorophyll"])
        df = df[["latitude", "longitude", "chlorophyll", "year"]]

        print(f"  → {len(df)} puntos válidos")
        datos_combinados.append(df)

# === COMBINAR TODOS LOS AÑOS ===
if datos_combinados:
    df_final = pd.concat(datos_combinados, ignore_index=True)
    df_final.to_csv(archivo_salida, index=False)
    print(f"\n✅ CSV generado con {len(df_final)} registros: {archivo_salida}")
else:
    print("❌ No se obtuvieron datos válidos de clorofila.")
