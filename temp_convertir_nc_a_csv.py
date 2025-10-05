import xarray as xr
import pandas as pd
import os
import re

# === CONFIGURACIÓN ===
carpeta = r"C:\Users\TuUsuario\Desktop\nasa\TuCarpetaConLosDatos"  # 🔹 Ruta donde están los .nc
archivo_salida = "temperatura_superficial.csv"

def extraer_año(nombre_archivo):
    match = re.search(r"20\d{2}", nombre_archivo)
    return int(match.group()) if match else None

# === PROCESAMIENTO ===
datos_combinados = []

for archivo in os.listdir(carpeta):
    if archivo.endswith(".nc"):
        ruta = os.path.join(carpeta, archivo)
        print(f"\nProcesando: {archivo}")
        ds = xr.open_dataset(ruta)

        da = ds["sst"]

        # Aplicar máscara para eliminar valores de relleno (_FillValue)
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
            "sst": "temperature"
        })

        # Mantener solo datos válidos
        df = df.dropna(subset=["temperature"])
        df = df[["latitude", "longitude", "temperature", "year"]]

        print(f"  → {len(df)} puntos válidos")
        datos_combinados.append(df)

# === COMBINAR TODOS LOS AÑOS ===
if datos_combinados:
    df_final = pd.concat(datos_combinados, ignore_index=True)
    df_final.to_csv(archivo_salida, index=False)
    print(f"\n✅ CSV generado con {len(df_final)} registros: {archivo_salida}")
else:
    print("❌ No se obtuvieron datos válidos de temperatura.")
