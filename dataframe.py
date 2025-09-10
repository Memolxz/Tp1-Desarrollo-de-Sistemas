import pandas as pd

sedes = pd.read_csv("./TablasLimpias/lista-sedes.csv", usecols=["sede_id", "pais_iso_3"])
print(sedes)

secciones = pd.read_csv("./TablasLimpias/lista-sedes-datos.csv", usecols=["sede_id"])
secciones.insert(0, "seccion_id", range(1, len(secciones) + 1))
print(secciones)

paises = pd.read_csv("./TablasLimpias/pbi-per-capita.csv", usecols=["Country Code", "Country Name", "2023"])
regiones = pd.read_csv("./TablasLimpias/lista-sedes-datos.csv", usecols=["region_geografica", "pais_iso_3"])
paises_regiones = pd.merge(paises, regiones, left_on="Country Code", right_on="pais_iso_3", how="inner")
paises_regiones = paises_regiones[["Country Code", "Country Name", "2023", "region_geografica"]]
print(paises)
print(regiones)
print(paises_regiones)

redes = pd.read_csv("./TablasLimpias/lista-sedes-datos.csv", usecols=["sede_id", "redes_sociales"])
redes_rows = []
id_counter = 1
for _, row in redes.iterrows():
    if pd.notna(row["redes_sociales"]):
        urls = [u.strip() for u in row["redes_sociales"].split(" // ") if u.strip()]
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
                "red_id": id_counter,
                "sede_id": row["sede_id"],
                "tipo": tipo,
                "url": url
            })
            id_counter += 1

redes = pd.DataFrame(redes_rows, columns=["red_id", "sede_id", "tipo", "url"])
print(redes)