# ============================================
# SMART ACADEMIC INTELLIGENCE DASHBOARD PRO MAX
# TODO corre desde Python
# ============================================

import pandas as pd
import json
from flask import Flask, render_template_string, request, jsonify, send_file
from io import StringIO
import os

app = Flask(__name__)

DATA_FILE = "datos_rendimiento_universidad_limpio.csv"
RESULT_FILE = "resultados.json"

# =====================================================
# 🔥 FUNCIÓN CENTRAL DE ANALISIS
# =====================================================

def generar_analisis(df):

    df["reprobado"] = df["calificacion"] < 6

    reprobacion_materia = (
        df.groupby("materia")["reprobado"]
        .mean() * 100
    ).sort_values(ascending=False)

    promedio_carrera = (
        df.groupby("carrera")["calificacion"]
        .mean()
        .sort_values(ascending=False)
    )

    promedio_estudiante = df.groupby("id_estudiante")["calificacion"].mean()

    reprobadas = (
        df[df["calificacion"] < 6]
        .groupby("id_estudiante")
        .size()
    )

    riesgo = pd.DataFrame({
        "promedio": promedio_estudiante,
        "reprobadas": reprobadas
    }).fillna(0)

    riesgo["en_riesgo"] = (
        (riesgo["promedio"] < 6.5) |
        (riesgo["reprobadas"] >= 1)
    )

    resultados = {
        "reprobacion_materia": reprobacion_materia.to_dict(),
        "promedio_carrera": promedio_carrera.to_dict(),
        "estudiantes_riesgo":
            riesgo[riesgo["en_riesgo"]]
            .reset_index()
            .to_dict(orient="records")
    }

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    return resultados


# Generar análisis inicial
if os.path.exists(DATA_FILE):
    df_init = pd.read_csv(DATA_FILE)
    generar_analisis(df_init)

# =====================================================
# 🎨 DASHBOARD HTML FULL ANIMADO
# =====================================================

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Smart Academic Intelligence Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body{
    background:linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
    font-family:system-ui;
}
.card{
    background:rgba(30,41,59,.9);
    backdrop-filter:blur(10px);
    border-radius:18px;
    padding:25px;
    box-shadow:0 20px 40px rgba(0,0,0,.6);
    transition:.4s;
}
.card:hover{
    transform:translateY(-6px) scale(1.02);
}
.glow{
    animation:glow 2s infinite alternate;
}
@keyframes glow{
    from{ text-shadow:0 0 10px #6366f1;}
    to{ text-shadow:0 0 25px #9333ea;}
}
</style>
</head>

<body class="p-10">

<h1 class="text-4xl font-bold mb-6 glow">
🚀 Smart Academic Intelligence Dashboard
</h1>

<div class="flex gap-3 mb-8">

<input type="file" id="fileInput" class="hidden">

<button onclick="document.getElementById('fileInput').click()"
class="bg-indigo-600 px-4 py-2 rounded hover:bg-indigo-500">
Importar CSV
</button>

<button onclick="exportJSON()"
class="bg-green-600 px-4 py-2 rounded hover:bg-green-500">
Exportar JSON
</button>

<button onclick="exportCSV()"
class="bg-green-700 px-4 py-2 rounded hover:bg-green-600">
Exportar CSV
</button>

<button onclick="descargarGrafica(chartM,'materias.png')"
class="bg-sky-600 px-4 py-2 rounded hover:bg-sky-500">
Descargar gráfico Materias
</button>

<button onclick="descargarGrafica(chartC,'carreras.png')"
class="bg-sky-700 px-4 py-2 rounded hover:bg-sky-600">
Descargar gráfico Carreras
</button>

</div>

<div class="grid md:grid-cols-2 gap-10">

<div class="card">
<h2 class="text-xl mb-4">Materias con mayor reprobación</h2>
<canvas id="chartMaterias"></canvas>
</div>

<div class="card">
<h2 class="text-xl mb-4">Promedio por Carrera</h2>
<canvas id="chartCarreras"></canvas>
</div>

</div>

<script>

let chartM;
let chartC;

async function cargarDatos(){
    const res = await fetch('/resultados');
    const data = await res.json();

    chartM = new Chart(document.getElementById('chartMaterias'),{
        type:'bar',
        data:{
            labels:Object.keys(data.reprobacion_materia),
            datasets:[{
                data:Object.values(data.reprobacion_materia),
                backgroundColor:'rgba(239,68,68,.85)',
                borderRadius:10
            }]
        },
        options:{animation:{duration:1500}}
    });

    chartC = new Chart(document.getElementById('chartCarreras'),{
        type:'line',
        data:{
            labels:Object.keys(data.promedio_carrera),
            datasets:[{
                data:Object.values(data.promedio_carrera),
                borderColor:'#6366f1',
                backgroundColor:'rgba(99,102,241,.2)',
                fill:true,
                tension:.4
            }]
        },
        options:{animation:{duration:1500}}
    });
}

document.getElementById("fileInput").addEventListener("change", async function(e){
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    await fetch("/upload",{
        method:"POST",
        body:formData
    });

    location.reload();
});

function exportJSON(){
    window.location.href="/export/json";
}

function exportCSV(){
    window.location.href="/export/csv";
}

function descargarGrafica(chart,filename){
    const url=chart.toBase64Image();
    const a=document.createElement("a");
    a.href=url;
    a.download=filename;
    a.click();
}

cargarDatos();

</script>

</body>
</html>
"""

# =====================================================
# 🚀 RUTAS
# =====================================================

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/resultados")
def resultados():
    with open(RESULT_FILE, encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    df = pd.read_csv(file)
    generar_analisis(df)
    return {"status":"ok"}

@app.route("/export/json")
def export_json():
    return send_file(RESULT_FILE, as_attachment=True)

@app.route("/export/csv")
def export_csv():
    with open(RESULT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    output = StringIO()
    output.write("seccion,clave,valor1,valor2\n")

    for k,v in data["reprobacion_materia"].items():
        output.write(f"materia,{k},{v},\n")

    for k,v in data["promedio_carrera"].items():
        output.write(f"carrera,{k},{v},\n")

    for s in data["estudiantes_riesgo"]:
        output.write(f"estudiante,{s['id_estudiante']},{s['promedio']},{s['reprobadas']}\n")

    output.seek(0)
    return send_file(
        StringIO(output.getvalue()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="resultados.csv"
    )

# =====================================================
# 🔥 INICIAR
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)