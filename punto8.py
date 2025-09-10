import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ======================
# Crear carpeta de gráficos
# ======================
os.makedirs("Graficos", exist_ok=True)

# Cargar datos
pais = pd.read_csv("modelos/pais.csv")
sedes = pd.read_csv("modelos/sedes.csv")

# --------------------------
# a) Cantidad de sedes por región
# --------------------------
sedes_region = (sedes
    .merge(pais, on="codigo_pais")
    .groupby("region")
    .agg(cantidad_sedes=("sede_id", "count"))
    .reset_index()
    .sort_values(by="cantidad_sedes", ascending=False)
)

plt.figure()
sns.barplot(x="region", y="cantidad_sedes", data=sedes_region)
plt.xticks(rotation=45)
plt.title("Cantidad de sedes por región")
plt.tight_layout()
plt.savefig("Graficos/8a_sedes_por_region.png")

# --------------------------
# b) Boxplot PBI per cápita por región
# --------------------------
plt.figure()
sns.boxplot(x="region", y="pbi_2023", data=pais.merge(sedes, on="codigo_pais"))
plt.xticks(rotation=45)
plt.title("Distribución PBI per cápita 2023 por región")
plt.tight_layout()
plt.savefig("Graficos/8b_boxplot_pbi.png")

# --------------------------
# c) Relación entre PBI y cantidad de sedes
# --------------------------
relacion = (sedes
    .groupby("codigo_pais")
    .agg(cantidad_sedes=("sede_id", "count"))
    .reset_index()
    .merge(pais, on="codigo_pais")
)

plt.figure()
sns.scatterplot(x="pbi_2023", y="cantidad_sedes", data=relacion)
plt.title("Relación entre PBI per cápita y cantidad de sedes")
plt.tight_layout()
plt.savefig("Graficos/8c_relacion_pbi_sedes.png")
