import psutil, os, stat, pwd, grp, subprocess


class CpuMonitor:
    def info(self):
        return {
            "percent":   psutil.cpu_percent(interval=0.3),
            "per_core":  psutil.cpu_percent(interval=0, percpu=True),
            "cores":     psutil.cpu_count(logical=True),
        }


class MemoryMonitor:
    def info(self):
        r = psutil.virtual_memory()
        return {
            "total_mb":  round(r.total   / 1024**2, 1),
            "used_mb":   round(r.used    / 1024**2, 1),
            "free_mb":   round(r.free    / 1024**2, 1),
            "percent":   r.percent,
        }


class ProcessManager:
    def list(self, search=""):
        procs = []
        for p in psutil.process_iter(["pid", "name", "username", "status", "cpu_percent", "memory_info"]):
            try:
                name = p.info["name"] or ""
                if search and search.lower() not in name.lower():
                    continue
                mem = p.info["memory_info"]
                procs.append({
                    "pid":    p.info["pid"],
                    "name":   name,
                    "user":   p.info["username"] or "",
                    "status": p.info["status"] or "",
                    "cpu":    round(p.info["cpu_percent"] or 0, 1),
                    "mem_mb": round(mem.rss / 1024**2, 1) if mem else 0,
                })
            except Exception:
                continue
        return sorted(procs, key=lambda x: x["mem_mb"], reverse=True)

    def kill(self, pid):
        try:
            psutil.Process(pid).terminate()
            return {"ok": True,  "msg": f"Processo {pid} encerrado."}
        except psutil.NoSuchProcess:
            return {"ok": False, "msg": "PID não encontrado."}
        except psutil.AccessDenied:
            return {"ok": False, "msg": "Permissão negada."}


class PermissionManager:
    def get(self, path):
        if not os.path.exists(path):
            return {"error": "Caminho não encontrado."}
        st = os.stat(path)
        m  = stat.S_IMODE(st.st_mode)
        try:   owner = pwd.getpwuid(st.st_uid).pw_name
        except: owner = str(st.st_uid)
        try:   group = grp.getgrgid(st.st_gid).gr_name
        except: group = str(st.st_gid)
        return {"octal": oct(m), "owner": owner, "group": group}

    def chmod(self, path, mode):
        try:
            os.chmod(path, int(mode, 8))
            return {"ok": True, "msg": f"chmod {mode} aplicado."}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def chown(self, path, owner):
        r = subprocess.run(["chown", owner, path], capture_output=True, text=True)
        if r.returncode == 0:
            return {"ok": True,  "msg": f"chown {owner} aplicado."}
        return {"ok": False, "msg": r.stderr.strip()}