import pandas as pd
import os

# ======================
# Crear carpetas si no existen
# ======================
os.makedirs("modelos", exist_ok=True)

# ======================
# Importar datasets originales
# ======================
pbi = pd.read_csv("TablasLimpias/pbi-per-capita.csv")             # Dataset PBI mundial
sedes = pd.read_csv("TablasLimpias/lista-sedes.csv")              # Datos básicos de sedes
sedes_datos = pd.read_csv("TablasLimpias/lista-sedes-datos.csv")  # Datos completos de sedes
secciones_orig = pd.read_csv("TablasLimpias/lista-secciones.csv") # Datos de secciones

# ======================
# Procesar tabla pais
# ======================
# Banco Mundial → código, nombre, PBI 2023
df_pbi = pbi[["Country Code", "Country Name", "2023"]].rename(columns={
    "Country Code": "codigo_pais",
    "Country Name": "nombre",
    "2023": "pbi_2023"
})

# Datos de Cancillería → región por país
df_region = sedes_datos[["pais_iso_3", "region_geografica"]].drop_duplicates()
df_region = df_region.rename(columns={
    "pais_iso_3": "codigo_pais",
    "region_geografica": "region"
})

# Merge de ambos (PBI + región)
df_pais = pd.merge(df_pbi, df_region, on="codigo_pais", how="inner")

# Eliminar nulos en PBI y región
df_pais = df_pais.dropna(subset=["pbi_2023", "region"]).reset_index(drop=True)

# ======================
# Procesar tabla sedes
# ======================
df_sedes = sedes[["sede_id", "pais_iso_3"]].dropna().reset_index(drop=True).rename(columns={
    "pais_iso_3": "codigo_pais"
})

# ======================
# Procesar tabla secciones con ID autoincrement
# ======================
secciones_rows = []
id_seccion = 1
for _, row in secciones_orig.iterrows():
    secciones_rows.append({
        "seccion_id": id_seccion,
        "sede_id": row["sede_id"]
    })
    id_seccion += 1
df_secciones = pd.DataFrame(secciones_rows)

# ======================
# Procesar tabla redes normalizada
# ======================
redes_rows = []
id_red = 1
for _, row in sedes_datos.iterrows():
    if pd.notna(row["redes_sociales"]):
        urls = [u.strip() for u in row["redes_sociales"].split(" // ") if u.strip()]
        for url in urls:
            url_low = url.lower()
            if "facebook" in url_low:
                tipo = "facebook"
            elif "twitter" in url_low:
                tipo = "twitter"
            elif "instagram" in url_low:
                tipo = "instagram"
            elif "youtube" in url_low:
                tipo = "youtube"
            else:
                tipo = "otra"

            redes_rows.append({
                "red_id": id_red,
                "sede_id": row["sede_id"],
                "nombre": tipo,
                "url": url
            })
            id_red += 1

df_redes = pd.DataFrame(redes_rows)

# ======================
# Guardar las tablas limpias
# ======================
df_pais.to_csv("modelos/pais.csv", index=False)
df_sedes.to_csv("modelos/sedes.csv", index=False)
df_secciones.to_csv("modelos/secciones.csv", index=False)
df_redes.to_csv("modelos/redes.csv", index=False)
