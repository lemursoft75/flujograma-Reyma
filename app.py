from flask import Flask, render_template, request, redirect
import json, os
from datetime import datetime
import webbrowser
import threading
import sys

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
app = Flask(__name__, template_folder=os.path.join(base_path, "templates"), static_folder=os.path.join(base_path, "static"))

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
    historial = cargar_historial()

    if request.method == "POST":
        nombre = request.form.get("nombre").strip()
        if nombre:
            if nombre not in clientes:
                hoy = datetime.today().strftime("%Y-%m-%d")
                clientes[nombre] = {
                    "estado": 0,
                    "fecha": hoy
                }
                if nombre in historial:
                    clientes[nombre]["ultima_entrega"] = historial[nombre]
            guardar_clientes(clientes)
        return redirect("/")

    return render_template("index.html", clientes=clientes, estados=ESTADOS)


def guardar_historial(nombre, fecha):
    archivo = "historial.json"
    historial = {}

    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            contenido = f.read().strip()
            if contenido:
                try:
                    historial = json.loads(contenido)
                except json.JSONDecodeError:
                    historial = {}

    historial[nombre] = fecha

    with open(archivo, "w") as f:
        json.dump(historial, f, indent=4)


@app.route("/avanzar/<nombre>")
def avanzar(nombre):
    clientes = cargar_clientes()
    if nombre in clientes and clientes[nombre]["estado"] < len(ESTADOS) - 1:
        clientes[nombre]["estado"] += 1
        guardar_clientes(clientes)
    return redirect("/")



def cargar_historial():
    archivo = "historial.json"
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            contenido = f.read().strip()
            if contenido:
                return json.loads(contenido)
            else:
                return {}
    return {}


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
        ultima_entrega = request.form.get("ultima_entrega", "").strip()

        clientes[nombre]["pedido"] = pedido
        clientes[nombre]["comentarios"] = comentarios
        clientes[nombre]["ultima_entrega"] = ultima_entrega  # ✅ Guardar fecha manual

        if ultima_entrega:
            guardar_historial(nombre, ultima_entrega)  # ✅ Guardar respaldo

        guardar_clientes(clientes)
    return redirect("/")


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        threading.Timer(1, open_browser).start()
        app.run(host='127.0.0.1', port=5000, debug=False)
    else:
        app.run(debug=True)