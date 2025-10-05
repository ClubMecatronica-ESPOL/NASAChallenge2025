import xarray as xr
import hvplot.xarray
import geoviews as gv
import panel as pn
import pandas as pd
import numpy as np
import holoviews as hv
import os
from pyproj import Transformer
from scipy.interpolate import interp1d

pn.extension('tabulator', 'plotly')

# === 1. Datos del tiburón ===
shark_file = "C:/Users/User/Downloads/NASA/data_challenge/tiburon/160424_2013_132346pnas_atn.csv"
df = pd.read_csv(shark_file)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Interpretar profundidad (lc -> 0-3, A/B -> NaN)
def parse_depth(x):
    try:
        return int(x)
    except:
        return np.nan

df["depth"] = df["lc"].apply(parse_depth)

# Transformar lon/lat a coordenadas métricas para interpolación
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
df["x"], df["y"] = transformer.transform(df["lon"].values, df["lat"].values)
df["t_s"] = (df["date"] - df["date"].iloc[0]).dt.total_seconds()

uniq = df.drop_duplicates(subset="t_s")
t = uniq["t_s"].values
depth_filled = uniq["depth"].ffill().bfill()

fx = interp1d(t, uniq["x"], kind="linear", fill_value="extrapolate")
fy = interp1d(t, uniq["y"], kind="linear", fill_value="extrapolate")
fz = interp1d(t, depth_filled, kind="nearest", fill_value="extrapolate")

# Interpolación cada 6h
t_new = np.arange(t.min(), t.max(), 6*3600)
x_new, y_new, z_new = fx(t_new), fy(t_new), fz(t_new)
z_new = np.round(z_new).astype(int)
z_new = np.clip(z_new, 0, 3)

# Convertir de nuevo a lon/lat
lon_new, lat_new = transformer.transform(x_new, y_new, direction="INVERSE")

# === 2. Datos de NASA ===
data_types = {
    "Temperatura": "C:/Users/User/Downloads/nasa/SeaTemps2025",
    "Clorofila": "C:/Users/User/Downloads/nasa/SeaChlorophyll2025"
}

type_widget = pn.widgets.Select(name="Tipo de dato", options=list(data_types.keys()), value="Temperatura")

def load_files(folder):
    nc_files = sorted([f for f in os.listdir(folder) if f.endswith(".nc")])
    datasets = {f: xr.open_dataset(os.path.join(folder, f)) for f in nc_files}
    return nc_files, datasets

nc_files, datasets = load_files(data_types[type_widget.value])
file_widget = pn.widgets.Select(name="Archivo", options=nc_files, value=nc_files[0])
var_widget = pn.widgets.Select(name="Variable", options=list(datasets[file_widget.value].data_vars))

def create_time_widget(ds):
    if "time" in ds.dims:
        return pn.widgets.DiscreteSlider(
            name="Índice de tiempo",
            options=list(range(len(ds["time"]))),
            value=0
        )
    else:
        return None

time_widget = create_time_widget(datasets[file_widget.value])

# --- Actualización de archivos cuando cambia tipo de dato ---
def update_files(event):
    global nc_files, datasets, time_widget
    folder = data_types[type_widget.value]
    nc_files, datasets = load_files(folder)
    file_widget.options = nc_files
    file_widget.value = nc_files[0]
    time_widget = create_time_widget(datasets[file_widget.value])

type_widget.param.watch(update_files, 'value')

# --- Actualización de variables cuando cambia archivo ---
def update_widgets(event):
    ds = datasets[event.new]
    var_widget.options = list(ds.data_vars)
    var_widget.value = list(ds.data_vars)[0]
    global time_widget
    time_widget = create_time_widget(ds)

file_widget.param.watch(update_widgets, 'value')

# --- Obtener dataset ---
def get_dataset():
    return datasets[file_widget.value]


# === FUNCIÓN PRINCIPAL DE VISUALIZACIÓN ===
def vista_func(var, t_index=0):
    ds = get_dataset()
    da = ds[var]
    if "time" in da.dims:
        da = da.isel(time=t_index)

    # === Configurar límites de color para clorofila ===
    clim = None
    if "chl" in var.lower() or "chlor" in var.lower():
        clim = (0, 1)

    # === Mapa base ===
    base = da.hvplot.quadmesh(
        x="lon", y="lat", rasterize=True, cmap="viridis",
        geo=True, coastline=True, projection="PlateCarree",
        clim=clim,
        title=f"{var} ({type_widget.value}) + Trayectoria del tiburón"
    )

    # === Trayectoria del tiburón ===
    shark_df = pd.DataFrame({
        'lon': lon_new,
        'lat': lat_new,
        'Profundidad': z_new
    })

    # Línea coloreada por profundidad
    shark_path = hv.Path(shark_df, kdims=['lon', 'lat'], vdims=['Profundidad']).opts(
        color='Profundidad', cmap=['blue', 'green', 'orange', 'red'],
        line_width=3, tools=['hover'], colorbar=True
    )

    # Puntos individuales
    shark_points = hv.Scatter(
        shark_df, kdims=['lon'], vdims=['lat', 'Profundidad']
    ).opts(
        color='Profundidad', cmap=['blue', 'green', 'orange', 'red'],
        size=5, alpha=0.8, marker='o', tools=['hover']
    )

    return base * shark_path * shark_points


# === Bind de widgets ===
if time_widget:
    vista = pn.bind(vista_func, var=var_widget, t_index=time_widget)
    widgets = [type_widget, file_widget, var_widget, time_widget]
else:
    vista = pn.bind(vista_func, var=var_widget)
    widgets = [type_widget, file_widget, var_widget]


# === LEYENDA ===
legend_text = """
### Codificación de Profundidades del Tiburón 🦈  
- **3 (Rojo):** Menor a 250 m (superficie)  
- **2 (Naranja):** Entre 250 y 500 m  
- **1 (Verde):** Entre 500 y 1500 m  
- **0 (Azul):** Mayor a 1500 m (zona profunda)
"""

# === LAYOUT FINAL ===
app = pn.Column(
    "# 🌎 Visualizador NASA + Trayectoria del tiburón",
    *widgets,
    vista,
    pn.pane.Markdown(legend_text)
)

app.show()
