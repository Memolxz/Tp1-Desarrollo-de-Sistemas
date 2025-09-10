import pandas as pd
import os
from pandasql import sqldf

# para ejecutar las querys con pandasql 
pysqldf = lambda q: sqldf(q, globals())

os.makedirs("Reportes", exist_ok=True)

# importar los datos
pais = pd.read_csv("modelos/pais.csv")
sedes = pd.read_csv("modelos/sedes.csv")
secciones = pd.read_csv("modelos/secciones.csv")
redes = pd.read_csv("modelos/redes.csv")

# 7 a
query_a = """
SELECT
  p.codigo_pais,
  p.nombre AS pais,
  COUNT(DISTINCT s.sede_id) AS cantidad_sedes,
  ROUND(
    CAST(COUNT(sec.seccion_id) AS FLOAT) / COUNT(DISTINCT s.sede_id),
    2
  ) AS promedio_secciones,
  p.pbi_2023
FROM sedes s
JOIN pais p ON s.codigo_pais = p.codigo_pais
LEFT JOIN secciones sec ON s.sede_id = sec.sede_id
GROUP BY p.codigo_pais, p.nombre, p.pbi_2023
ORDER BY cantidad_sedes DESC, pais ASC;
"""
reporte_a = pysqldf(query_a)
reporte_a.to_csv("Reportes/reporte_7a.csv", index=False)
print("Generado Reportes/reporte_7a.csv")

# 7 b
query_b = """
WITH paises_region AS (
  SELECT DISTINCT p.codigo_pais, p.region, p.pbi_2023
  FROM pais p
  JOIN sedes s ON p.codigo_pais = s.codigo_pais
),
paises_por_region AS (
  SELECT p.region, COUNT(DISTINCT p.codigo_pais) AS cantidad_paises
  FROM pais p
  JOIN sedes s ON p.codigo_pais = s.codigo_pais
  GROUP BY p.region
),
pbi_region AS (
  SELECT region, AVG(pbi_2023) AS promedio_pbi
  FROM paises_region
  GROUP BY region
)
SELECT prg.region, prg.cantidad_paises, pr.promedio_pbi
FROM paises_por_region prg
JOIN pbi_region pr ON prg.region = pr.region
ORDER BY pr.promedio_pbi DESC;
"""
reporte_b = pysqldf(query_b)
reporte_b.to_csv("Reportes/reporte_7b.csv", index=False)
print("Generado Reportes/reporte_7b.csv")

# 7 c
query_c = """
SELECT
  p.nombre AS pais,
  COUNT(DISTINCT r.nombre) AS cantidad_tipos_redes
FROM pais p
LEFT JOIN sedes s ON p.codigo_pais = s.codigo_pais
LEFT JOIN redes r ON s.sede_id = r.sede_id
GROUP BY p.nombre
ORDER BY pais;
"""
reporte_c = pysqldf(query_c)
reporte_c.to_csv("Reportes/reporte_7c.csv", index=False)
print("Generado Reportes/reporte_7c.csv")


# 7 d
query_d = """
SELECT
  p.nombre AS pais,
  s.sede_id,
  r.nombre AS red_social,
  r.url
FROM pais p
JOIN sedes s ON p.codigo_pais = s.codigo_pais
JOIN redes r ON s.sede_id = r.sede_id
ORDER BY pais ASC, s.sede_id ASC, red_social ASC, r.url ASC;
"""
reporte_d = pysqldf(query_d)
reporte_d.to_csv("Reportes/reporte_7d.csv", index=False)
print("Generado Reportes/reporte_7d.csv")