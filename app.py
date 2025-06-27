from flask import Flask, render_template, request, redirect
import json, os
from datetime import datetime

app = Flask(__name__)
ARCHIVO_JSON = "clientes.json"

ESTADOS = ["cotizar", "aprobar", "liberar", "embarcar", "notificar", "facturar", "finalizado"]

def cargar_clientes():
    if os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "r") as f:
            return json.load(f)
    return {}

def guardar_clientes(clientes):
    with open(ARCHIVO_JSON, "w") as f:
        json.dump(clientes, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    clientes = cargar_clientes()

    if request.method == "POST":
        nombre = request.form.get("nombre").strip()
        if nombre and nombre not in clientes:
            hoy = datetime.today().strftime("%Y-%m-%d")
            clientes[nombre] = {"estado": 0, "fecha": hoy}
            guardar_clientes(clientes)
        return redirect("/")

    return render_template("index.html", clientes=clientes, estados=ESTADOS)

@app.route("/avanzar/<nombre>")
def avanzar(nombre):
    clientes = cargar_clientes()
    if nombre in clientes and clientes[nombre]["estado"] < len(ESTADOS) - 1:
        clientes[nombre]["estado"] += 1
        guardar_clientes(clientes)
    return redirect("/")

@app.route("/eliminar/<nombre>")
def eliminar(nombre):
    clientes = cargar_clientes()
    if nombre in clientes:
        del clientes[nombre]
        guardar_clientes(clientes)
    return redirect("/")

@app.route("/editar/<nombre>", methods=["POST"])
def editar(nombre):
    clientes = cargar_clientes()
    if nombre in clientes:
        pedido = request.form.get("pedido", "").strip()
        comentarios = request.form.get("comentarios", "").strip()
        clientes[nombre]["pedido"] = pedido
        clientes[nombre]["comentarios"] = comentarios
        guardar_clientes(clientes)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)