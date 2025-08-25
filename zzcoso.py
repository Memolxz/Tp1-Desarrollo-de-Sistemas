import pandas as pd
import numpy as np

# =========================
# 1. Cargar datasets originales
# =========================
sedes = pd.read_csv("lista-sedes.csv")
sedes_datos = pd.read_csv("lista-sedes-datos.csv")
secciones = pd.read_csv("lista-secciones.csv")
pbi = pd.read_csv("API_NY.GDP.PCAP.CD_DS2_en_csv_v2_376305.csv", skiprows=4)

# =========================
# 2. Procesamiento y limpieza
# =========================

# ---- PBI (Banco Mundial) ----
# Imputar valores faltantes de 2023 con el último año válido (forward-fill)
pbi_ffill = pbi.copy()
pbi_ffill.iloc[:, 4:] = pbi_ffill.iloc[:, 4:].ffill(axis=1)  # solo columnas de años
pbi_2023 = pbi_ffill[["Country Code", "Country Name", "2023"]].rename(
    columns={"Country Code": "pais_iso_3", "Country Name": "nombre", "2023": "pbi_2023"}
)

# ---- Países ----
paises = sedes_datos[["pais_iso_3", "pais_castellano", "region_geografica"]].drop_duplicates()
paises = paises.rename(columns={"pais_castellano": "nombre", "region_geografica": "region"})

pbi_2023 = pbi_2023.rename(columns={"nombre": "nombre_pbi"}) #dsp ver bien tdo eso de los nombres q lo q hizo tito es un lio
df_pais = paises.merge(pbi_2023, on="pais_iso_3", how="left")

# ---- Sedes ----
df_sede = sedes[["sede_id", "sede_desc_castellano", "ciudad_castellano", "sede_tipo", "pais_iso_3"]].rename(
    columns={
        "sede_desc_castellano": "nombre",
        "ciudad_castellano": "ciudad",
        "sede_tipo": "tipo"
    }
)

# ---- Secciones ----
df_seccion = secciones[["sede_id", "tipo_seccion", "nombre_titular", "apellido_titular", "cargo_titular"]].copy()
df_seccion = df_seccion.rename(columns={
    "tipo_seccion": "tipo",
    "nombre_titular": "titular_nombre",
    "apellido_titular": "titular_apellido",
    "cargo_titular": "cargo"
})
df_seccion.insert(0, "id_seccion", range(1, len(df_seccion) + 1))

# Eliminar duplicados de secciones
df_seccion = df_seccion.drop_duplicates(subset=["sede_id", "tipo", "titular_nombre", "titular_apellido"])

# ---- Redes sociales ----
redes_rows = []
id_counter = 1
for _, row in sedes_datos.iterrows():
    if pd.notna(row["redes_sociales"]):
        urls = [u.strip() for u in row["redes_sociales"].split("//") if u.strip()]
        for url in urls:
            # Identificar tipo de red
            if "facebook" in url.lower():
                tipo = "facebook"
            elif "twitter" in url.lower():
                tipo = "twitter"
            elif "instagram" in url.lower():
                tipo = "instagram"
            elif "youtube" in url.lower():
                tipo = "youtube"
            else:
                tipo = "otra"
            redes_rows.append({
                "id_red": id_counter,
                "sede_id": row["sede_id"],
                "tipo": tipo,
                "url": url
            })
            id_counter += 1

df_redes = pd.DataFrame(redes_rows, columns=["id_red", "sede_id", "tipo", "url"])

# Eliminar duplicados de redes sociales por sede
df_redes = df_redes.drop_duplicates(subset=["sede_id", "url"])

# =========================
# 3. DataFrames finales listos para usar
# =========================
print("Países:", df_pais, "\n")
print("Sedes:", df_sede, "\n")
print("Secciones:", df_seccion, "\n")
print("Redes Sociales:", df_redes, "\n")

# =========================
# Reporte a) Por país
# =========================
# cantidad de sedes
sedes_por_pais = df_sede.groupby("pais_iso_3").size().reset_index(name="cant_sedes")

# promedio de secciones por sede
secciones_por_sede = df_seccion.groupby("sede_id").size().reset_index(name="cant_secciones")
promedio_secciones = df_sede.merge(secciones_por_sede, on="sede_id", how="left").fillna(0)
promedio_secciones = promedio_secciones.groupby("pais_iso_3")["cant_secciones"].mean().reset_index(name="promedio_secciones")

# unir con PBI
reporte_a = df_pais[["pais_iso_3", "nombre", "pbi_2023"]] \
    .merge(sedes_por_pais, on="pais_iso_3") \
    .merge(promedio_secciones, on="pais_iso_3")

# ordenar: primero por cantidad de sedes (desc), luego por nombre (asc)
reporte_a = reporte_a.sort_values(by=["cant_sedes", "nombre"], ascending=[False, True])

# =========================
# Reporte b) Por región
# =========================
# países con al menos una sede
paises_con_sede = df_sede[["pais_iso_3"]].drop_duplicates()
regiones = df_pais.merge(paises_con_sede, on="pais_iso_3")
reporte_b = regiones.groupby("region").agg(
    cant_paises=("pais_iso_3", "nunique"),
    promedio_pbi=("pbi_2023", "mean")
).reset_index().sort_values(by="promedio_pbi")

# =========================
# Reporte c) Variedad de redes sociales por país
# =========================
redes_pais = df_redes.merge(df_sede[["sede_id", "pais_iso_3"]], on="sede_id")
reporte_c = redes_pais.groupby("pais_iso_3")["tipo"].nunique().reset_index(name="variedad_redes")
reporte_c = reporte_c.merge(df_pais[["pais_iso_3", "nombre"]], on="pais_iso_3")

# =========================
# Reporte d) Detalle de redes sociales
# =========================
reporte_d = df_redes.merge(df_sede[["sede_id", "nombre", "pais_iso_3"]], on="sede_id") \
    .merge(df_pais[["pais_iso_3", "nombre"]].rename(columns={"nombre": "pais"}), on="pais_iso_3") \
    .sort_values(by=["pais", "nombre", "tipo", "url"]) \
    [["pais", "nombre", "tipo", "url"]]

# =========================
# Mostrar resultados
# =========================
print("Reporte A - Por país:\n", reporte_a, "\n")
print("Reporte B - Por región:\n", reporte_b, "\n")
print("Reporte C - Redes por país:\n", reporte_c, "\n")
print("Reporte D - Redes detalle:\n", reporte_d, "\n")

import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# a) Cantidad de sedes por región
# =========================
sedes_region = df_sede.merge(df_pais[["pais_iso_3", "region"]], on="pais_iso_3")
sedes_region_count = sedes_region.groupby("region").size().reset_index(name="cant_sedes")
sedes_region_count = sedes_region_count.sort_values(by="cant_sedes", ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(data=sedes_region_count, x="region", y="cant_sedes", palette="viridis")
plt.xticks(rotation=45, ha="right")
plt.title("Cantidad de sedes por región geográfica")
plt.ylabel("Cantidad de sedes")
plt.xlabel("Región geográfica")
plt.tight_layout()
plt.show()

# =========================
# b) Boxplot PBI per cápita 2023 por región
# =========================
# Solo países con al menos una sede
pbi_region = df_pais.merge(df_sede[["pais_iso_3"]].drop_duplicates(), on="pais_iso_3")

plt.figure(figsize=(10,6))
sns.boxplot(data=pbi_region, x="region", y="pbi_2023", palette="Set2")
plt.xticks(rotation=45, ha="right")
plt.title("Distribución del PBI per cápita 2023 por región (países con sedes)")
plt.ylabel("PBI per cápita (USD)")
plt.xlabel("Región geográfica")
plt.tight_layout()
plt.show()

# =========================
# c) Relación entre PBI y cantidad de sedes
# =========================
sedes_count = df_sede.groupby("pais_iso_3").size().reset_index(name="cant_sedes")
pbi_sedes = df_pais.merge(sedes_count, on="pais_iso_3", how="left").fillna(0)

plt.figure(figsize=(8,6))
sns.scatterplot(data=pbi_sedes, x="pbi_2023", y="cant_sedes", hue="region")
plt.xscale("log")  # escala log para PBI (hay mucha variación)
plt.title("Relación entre PBI per cápita (2023) y cantidad de sedes argentinas")
plt.xlabel("PBI per cápita (USD, escala log)")
plt.ylabel("Cantidad de sedes")
plt.legend(title="Región", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()
