from flask import Flask, jsonify, request
from flask_cors import CORS
from monitor import CpuMonitor, MemoryMonitor, ProcessManager, PermissionManager

app = Flask(__name__)
CORS(app)

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