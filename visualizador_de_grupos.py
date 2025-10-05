import pandas as pd
import hvplot.pandas
import panel as pn

pn.extension()

# === 1. Cargar datos ===
df = pd.read_csv("datosCombiandosDeTemperaturaClorofila.csv")
tib = pd.read_csv("DatosDeTiburones.csv")

df = df.dropna(subset=["temperature", "chlorophyll"])
tib = tib.dropna(subset=["latitude", "longitude"])

# === 2. Widgets ===
año_widget = pn.widgets.IntSlider(
    name="Año", start=int(df["year"].min()), end=int(df["year"].max()), step=1, value=int(df["year"].min())
)
variable_widget = pn.widgets.Select(
    name="Variable oceánica", options=["temperature", "chlorophyll"], value="temperature"
)
especie_widget = pn.widgets.MultiSelect(
    name="Especie de tiburón", options=tib["species"].unique().tolist(), value=tib["species"].unique().tolist()
)

# === 3. Función de actualización ===
@pn.depends(año=año_widget, variable=variable_widget, especie=especie_widget)
def vista_mapa(año, variable, especie):
    datos_año = df[df["year"] == año]
    tib_año = tib[(tib["year"] == año) & (tib["species"].isin(especie))]

    # Limitar color para clorofila y temperatura
    if variable == "chlorophyll":
        clim = (0, 0.5)  # la mayoría de valores útiles de clorofila
        cmap = "Greens"
    elif variable == "temperature":
        clim = (0, 35)  # opcional: limita temperatura para destacar océano
        cmap = "viridis"
    else:
        clim = None
        cmap = "viridis"

    # Capa oceánica
    mapa = datos_año.hvplot.points(
        x="longitude",
        y="latitude",
        c=variable,
        geo=True,
        tiles="OSM",
        colorbar=True,
        cmap=cmap,
        alpha=0.6,
        frame_width=800,
        frame_height=450,
        clim=clim  # ✅ aplicar límite de color
    )

    # Tiburones
    tib_plot = tib_año.hvplot.points(
        x="longitude",
        y="latitude",
        geo=True,
        color="red",
        size=10,
        marker="triangle",
        alpha=0.8,
        hover_cols=["id", "species", "year"]
    )

    return mapa * tib_plot


# === 4. Layout ===
app = pn.Column(
    "# 🦈 Tiburones y Datos Oceánicos",
    pn.Row(año_widget, variable_widget, especie_widget),
    vista_mapa
)

app.show()