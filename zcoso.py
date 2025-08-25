import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sedes = pd.read_csv("lista-sedes.csv")
sedes_datos = pd.read_csv("lista-sedes-datos.csv")
secciones = pd.read_csv("lista-secciones.csv")
pbi = pd.read_csv("API_NY.GDP.PCAP.CD_DS2_en_csv_v2_376305.csv", skiprows=4)

df_pais = pd.DataFrame(columns=[
    "pais_id",   # PK
    "nombre",
    "region",
    "pbi_2023"
])

df_sede = pd.DataFrame(columns=[
    "sede_id",      # PK
    "nombre",
    "ciudad",
    "tipo",
    "pais_id"    # FK -> País
])

df_seccion = pd.DataFrame(columns=[
    "id_seccion",   # PK (autogenerado)
    "sede_id",      # FK -> Sede
    "tipo",
    "titular_nombre",
    "titular_apellido",
    "cargo"
])

df_redes = pd.DataFrame(columns=[
    "id_red",       # PK (autogenerado)
    "sede_id",      # FK -> Sede
    "tipo",
    "url"
])


pbi_2023 = pbi[["Country Code", "Country Name", "2023"]].rename(
    columns={"Country Code": "pais_id", "Country Name": "nombre", "2023": "pbi_2023"}
)

sedes_datos = sedes_datos.rename(columns={"pais_iso_3": "pais_id"})
paises = sedes_datos[["pais_id", "pais_castellano", "region_geografica"]].drop_duplicates()
paises = paises.rename(columns={"pais_castellano": "nombre", "region_geografica": "region"})

pbi_2023 = pbi_2023.rename(columns={"nombre": "nombre_pbi"}) #dsp ver bien tdo eso de los nombres q lo q hizo tito es un lio
df_pais = paises.merge(pbi_2023, on="pais_id", how="left")

df_sede = sedes[["sede_id", "sede_desc_castellano", "ciudad_castellano", "sede_tipo", "pais_iso_3"]].rename(
    columns={
        "sede_desc_castellano": "nombre",
        "ciudad_castellano": "ciudad",
        "sede_tipo": "tipo",
        "pais_iso_3": "pais_id"
    }
)

df_seccion = secciones[["sede_id", "tipo_seccion", "nombre_titular", "apellido_titular", "cargo_titular"]].copy()
df_seccion = df_seccion.rename(columns={
    "tipo_seccion": "tipo",
    "nombre_titular": "titular_nombre",
    "apellido_titular": "titular_apellido",
    "cargo_titular": "cargo"
})
df_seccion.insert(0, "id_seccion", range(1, len(df_seccion) + 1))

redes_rows = []
id_counter = 1
for _, row in sedes_datos.iterrows():
    if pd.notna(row["redes_sociales"]):
        urls = [u.strip() for u in row["redes_sociales"].split("//") if u.strip()]
        for url in urls:
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
                "url": url.strip()
            })
            id_counter += 1

df_redes = pd.DataFrame(redes_rows, columns=["id_red", "sede_id", "tipo", "url"])

print("País:", df_pais, "\n")
print("Sede:", df_sede, "\n")
print("Sección:", df_seccion, "\n")
print("Redes Sociales:", df_redes, "\n")


# cantidad de sedes
sedes_por_pais = df_sede.groupby("pais_id").size().reset_index(name="cant_sedes")

# promedio de secciones por sede
secciones_por_sede = df_seccion.groupby("sede_id").size().reset_index(name="cant_secciones")
promedio_secciones = df_sede.merge(secciones_por_sede, on="sede_id", how="left").fillna(0)
promedio_secciones = promedio_secciones.groupby("pais_id")["cant_secciones"].mean().reset_index(name="promedio_secciones")

# unir con PBI
reporte_a = df_pais[["pais_id", "nombre", "pbi_2023"]].merge(sedes_por_pais, on="pais_id") \
                                                        .merge(promedio_secciones, on="pais_id")

# ordenar
reporte_a = reporte_a.sort_values(by=["cant_sedes", "nombre"], ascending=[False, True])

# =========================
# Reporte b) Por región
# =========================
# cantidad de países con al menos una sede
paises_con_sede = df_sede[["pais_id"]].drop_duplicates()
regiones = df_pais.merge(paises_con_sede, on="pais_id")
reporte_b = regiones.groupby("region").agg(
    cant_paises=("pais_id", "nunique"),
    promedio_pbi=("pbi_2023", "mean")
).reset_index().sort_values(by="promedio_pbi")

# =========================
# Reporte c) Variedad de redes sociales por país
# =========================
# unir sedes con redes
redes_pais = df_redes.merge(df_sede[["sede_id", "pais_id"]], on="sede_id")
reporte_c = redes_pais.groupby("pais_id")["tipo"].nunique().reset_index(name="variedad_redes")
reporte_c = reporte_c.merge(df_pais[["pais_id", "nombre"]], on="pais_id")

# =========================
# Reporte d) Detalle de redes sociales
# =========================
reporte_d = df_redes.merge(df_sede[["sede_id", "pais_id"]], on="sede_id") \
                    .merge(df_pais[["pais_id", "nombre"]].rename(columns={"nombre": "pais"}), on="pais_id") \
                    .sort_values(by=["pais", "sede_id", "tipo", "url"]) \
                    [["pais", "sede_id", "tipo", "url"]]

# =========================
# Mostrar resultados
# =========================
print("Reporte A - Por país:\n", reporte_a, "\n")
print("Reporte B - Por región:\n", reporte_b, "\n")
print("Reporte C - Redes por país:\n", reporte_c, "\n")
print("Reporte D - Redes detalle:\n", reporte_d, "\n")

# =========================
# a) Cantidad de sedes por región
# =========================
sedes_region = df_sede.merge(df_pais[["pais_id", "region"]], on="pais_id")
sedes_region_count = sedes_region.groupby("region").size().reset_index(name="cant_sedes")
sedes_region_count = sedes_region_count.sort_values(by="cant_sedes", ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(data=sedes_region_count, x="region", y="cant_sedes", palette="viridis")
plt.xticks(rotation=45, ha="right")
plt.title("Cantidad de sedes por región geográfica")
plt.tight_layout()
plt.show()

# =========================
# b) Boxplot PBI per cápita 2023 por región
# =========================
pbi_region = df_pais.merge(df_sede[["pais_id"]].drop_duplicates(), on="pais_id")
plt.figure(figsize=(10,6))
sns.boxplot(data=pbi_region, x="region", y="pbi_2023", palette="Set2")
plt.xticks(rotation=45, ha="right")
plt.title("Distribución del PBI per cápita 2023 por región (con sedes)")
plt.tight_layout()
plt.show()

# =========================
# c) Relación entre PBI y cantidad de sedes
# =========================
sedes_count = df_sede.groupby("pais_id").size().reset_index(name="cant_sedes")
pbi_sedes = df_pais.merge(sedes_count, on="pais_id", how="left").fillna(0)

plt.figure(figsize=(8,6))
sns.scatterplot(data=pbi_sedes, x="pbi_2023", y="cant_sedes", hue="region")
plt.xscale("log")  # escala log para PBI porque hay mucha variación
plt.title("Relación entre PBI per cápita (2023) y cantidad de sedes argentinas")
plt.xlabel("PBI per cápita (USD, escala log)")
plt.ylabel("Cantidad de sedes")
plt.tight_layout()
plt.show()