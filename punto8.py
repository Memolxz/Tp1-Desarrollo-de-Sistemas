import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("Graficos", exist_ok=True)

# importar los datos
pais = pd.read_csv("Modelos/pais.csv")
redes = pd.read_csv("Modelos/redes.csv")
secciones = pd.read_csv("Modelos/secciones.csv")
sedes = pd.read_csv("Modelos/sedes.csv")

# mergear sedes con países para tener región y pbi
sedes_pais = sedes.merge(pais, on="codigo_pais", how="left")

# 8 a
sedes_por_region = sedes_pais.groupby("region").size().reset_index(name="cantidad")
sedes_por_region = sedes_por_region.sort_values(by="cantidad", ascending=False)

plt.figure(figsize=(10,6))
ax = sns.barplot(data=sedes_por_region, x="region", y="cantidad", palette="viridis")

for p in ax.patches:
    ax.annotate(
        f"{int(p.get_height())}", 
        (p.get_x() + p.get_width() / 2., p.get_height()), 
        ha="center", va="bottom", fontsize=10, fontweight="bold", color="black"
    )

plt.xticks(rotation=45, ha="right")
plt.title("Cantidad de sedes por region", fontsize=14, weight="bold")
plt.xlabel("Region geografica")
plt.ylabel("Cantidad de sedes")
plt.tight_layout()
plt.savefig("Graficos/8a.png", dpi=300)
plt.close()

# 8 b
paises_con_delegacion = pd.Series(sedes["codigo_pais"].unique())
pbi_paises = pais[pais["codigo_pais"].isin(paises_con_delegacion)].dropna(subset=["pbi_2023"]).copy()

orden_regiones = (
    pbi_paises.groupby("region")["pbi_2023"]
    .median()
    .sort_values()
    .index
)

plt.figure(figsize=(10,6))
sns.boxplot(
    data=pbi_paises,
    x="region",
    y="pbi_2023",
    order=orden_regiones,
    palette="Set2"
)
plt.xticks(rotation=45, ha="right")
plt.title("PBI per cápita 2023 por región", fontsize=12, weight="bold")
plt.xlabel("Región geográfica", fontsize=10)
plt.ylabel("PBI per cápita 2023 (USD)", fontsize=10)
plt.tight_layout()
plt.savefig("Graficos/8b.png", dpi=300)
plt.close()

# 8 c
sedes_por_pais = sedes.groupby("codigo_pais").size().reset_index(name="cantidad_sedes")
pbi_sedes_pais = sedes_por_pais.merge(pais, on="codigo_pais", how="left")

plt.figure(figsize=(10,6))
sns.scatterplot(
    data=pbi_sedes_pais, 
    x="pbi_2023", 
    y="cantidad_sedes", 
    hue="region", 
    palette="tab10", 
    alpha=0.8, 
    s=100
)
plt.title("Relacion entre PBI per capita y cantidad de sedes por país", fontsize=14, weight="bold")
plt.xlabel("PBI per capita 2023")
plt.ylabel("Cantidad de sedes")
plt.tight_layout()
plt.savefig("Graficos/8c.png", dpi=300)
plt.close()

print("se generaron los graficos")
