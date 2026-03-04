# Carlos Rebollar Pineda
# sergio Adriel Muñoz Camarena

import pandas as pd
import matplotlib.pyplot as plt

print("=== ANÁLISIS SIMPLE DE RENDIMIENTO ===\n")
df = pd.read_csv("datos_rendimiento_universidad_limpio.csv")
print("Datos cargados.\n")

# 1) % de reprobación por materia
# Hago una columna booleana y luego el promedio (True=1 => %)
df["reprobado"] = df["calificacion"] < 6
reprobacion_materia = (df.groupby("materia")["reprobado"].mean() * 100).sort_values(ascending=False)
print("Reprobación por materia (%)")
print(reprobacion_materia, "\n")

plt.figure()
reprobacion_materia.plot(kind="bar")
plt.title("Reprobación por materia (%)")
plt.ylabel("%")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2) Promedio por carrera
promedio_carrera = df.groupby("carrera")["calificacion"].mean().sort_values(ascending=False)
print("Promedio por carrera")
print(promedio_carrera, "\n")

plt.figure()
promedio_carrera.plot(kind="bar")
plt.title("Promedio por carrera")
plt.ylabel("Promedio")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3) Tendencia por semestre (¿mejoran o empeoran?)
promedio_semestre = df.groupby("semestre")["calificacion"].mean()
print("Promedio por semestre")
print(promedio_semestre, "\n")

plt.figure()
promedio_semestre.plot(marker="o")
plt.title("Promedio por semestre")
plt.xlabel("Semestre")
plt.ylabel("Promedio")
plt.tight_layout()
plt.show()

# 4) Detectar estudiantes en riesgo
# Criterio: promedio < 6.5 o al menos 1  matetia reprobada
promedio_estudiante = df.groupby("id_estudiante")["calificacion"].mean()
reprobadas = df[df["calificacion"] < 6].groupby("id_estudiante").size()
riesgo = pd.DataFrame({"promedio": promedio_estudiante, "reprobadas": reprobadas}).fillna(0)
riesgo["en_riesgo"] = (riesgo["promedio"] < 6.5) | (riesgo["reprobadas"] >= 1)

print("Estudiantes en riesgo (lista breve)")
print(riesgo[riesgo["en_riesgo"]])