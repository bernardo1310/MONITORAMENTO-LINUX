from flask import Flask, jsonify, request
from flask_cors import CORS
from monitor import CpuMonitor, MemoryMonitor, ProcessManager, PermissionManager

app = Flask(__name__)
CORS(app)
from flask import Flask, jsonify, request
from flask_cors import CORS
from monitor import CpuMonitor, MemoryMonitor, ProcessManager, PermissionManager

app = Flask(__name__)
CORS(app)  # permite o index.html (porta 8080) falar com a API (porta 5000)

# instancia as classes uma vez, ficam vivas enquanto o servidor estiver rodando
cpu  = CpuMonitor()
mem  = MemoryMonitor()
proc = ProcessManager()
perm = PermissionManager()


# --- CPU ---

@app.route("/api/cpu")
def route_cpu():
    return jsonify(cpu.info())


# --- Memória ---

@app.route("/api/memory")
def route_memory():
    return jsonify(mem.info())


# --- Processos ---

@app.route("/api/processes")
def route_processes():
    # ?search=nome filtra por nome, se não vier retorna tudo
    search = request.args.get("search", "")
    return jsonify(proc.list(search))


@app.route("/api/processes/<int:pid>", methods=["DELETE"])
def route_kill(pid):
    result = proc.kill(pid)
    # retorna 200 se encerrou, 400 se deu erro
    status = 200 if result["ok"] else 400
    return jsonify(result), status


# --- Permissões ---

@app.route("/api/permissions")
def route_get_perm():
    # ?path=/caminho/do/arquivo
    path = request.args.get("path", "")
    return jsonify(perm.get(path))


@app.route("/api/permissions", methods=["POST"])
def route_set_perm():
    data  = request.json or {}
    path  = data.get("path", "")
    mode  = data.get("mode", "")   # ex: "755"
    owner = data.get("owner", "")  # ex: "user:grupo"

    if mode:
        result = perm.chmod(path, mode)
        if not result["ok"]:
            return jsonify(result), 400

    if owner:
        result = perm.chown(path, owner)
        if not result["ok"]:
            return jsonify(result), 400

    return jsonify({"ok": True, "msg": "Permissões atualizadas."})


# --- inicia o servidor ---

if __name__ == "__main__":
    app.run(port=5000, debug=True)
cpu  = CpuMonitor()
mem  = MemoryMonitor()
proc = ProcessManager()
perm = PermissionManager()

@app.route("/api/cpu")
def route_cpu():
    return jsonify(cpu.info())

@app.route("/api/memory")
def route_memory():
    return jsonify(mem.info())

@app.route("/api/processes")
def route_processes():
    return jsonify(proc.list(request.args.get("search", "")))

@app.route("/api/processes/<int:pid>", methods=["DELETE"])
def route_kill(pid):
    result = proc.kill(pid)
    return jsonify(result), (200 if result["ok"] else 400)

@app.route("/api/permissions")
def route_get_perm():
    return jsonify(perm.get(request.args.get("path", "")))

@app.route("/api/permissions", methods=["POST"])
def route_set_perm():
    d = request.json or {}
    path, mode, owner = d.get("path",""), d.get("mode",""), d.get("owner","")
    if mode:
        r = perm.chmod(path, mode)
        if not r["ok"]: return jsonify(r), 400
    if owner:
        r = perm.chown(path, owner)
        if not r["ok"]: return jsonify(r), 400
    return jsonify({"ok": True, "msg": "Permissões atualizadas."})

if __name__ == "__main__":
    app.run(port=5000, debug=True)