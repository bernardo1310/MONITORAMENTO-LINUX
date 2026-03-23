import psutil      # lê dados do sistema: CPU, memória, processos
import os          # trabalha com arquivos e pastas
import stat        # interpreta as permissões de arquivos
import pwd         # pega o nome do dono de um arquivo
import grp         # pega o nome do grupo de um arquivo
import subprocess  # executa comandos no terminal (usado no chown)

class CpuMonitor:
    # lê os dados de CPU direto do sistema via psutil
    def info(self):
        return {
            "percent":  psutil.cpu_percent(interval=0.3),        # uso geral, aguarda 0.3s para precisão
            "per_core": psutil.cpu_percent(interval=0, percpu=True),  # uso de cada núcleo
            "cores":    psutil.cpu_count(logical=True),           # total de núcleos lógicos
        }


class MemoryMonitor:
    # lê o uso de memória RAM
    def info(self):
        mem = psutil.virtual_memory()

        # converte bytes para MB
        def to_mb(value):
            return round(value / 1024 / 1024, 1)

        return {
            "total_mb": to_mb(mem.total),   # total de RAM da máquina
            "used_mb":  to_mb(mem.used),    # quanto está sendo usado agora
            "free_mb":  to_mb(mem.free),    # quanto está livre
            "percent":  mem.percent,        # % de uso, já vem calculado
        }


class ProcessManager:
    # retorna lista de processos, com filtro opcional por nome
    def list(self, search=""):
        procs = []

        fields = ["pid", "name", "username", "status", "cpu_percent", "memory_info"]

        for p in psutil.process_iter(fields):
            try:
                name = p.info["name"] or ""

                # ignora se não bater com o filtro
                if search and search.lower() not in name.lower():
                    continue

                mem    = p.info["memory_info"]
                mem_mb = round(mem.rss / 1024 / 1024, 1) if mem else 0

                procs.append({
                    "pid":    p.info["pid"],
                    "name":   name,
                    "user":   p.info["username"] or "",
                    "status": p.info["status"] or "",
                    "cpu":    round(p.info["cpu_percent"] or 0, 1),
                    "mem_mb": mem_mb,
                })

            except Exception:
                # processo pode sumir ou negar acesso durante a leitura
                continue

        # ordena do que usa mais memória para o que usa menos
        return sorted(procs, key=lambda x: x["mem_mb"], reverse=True)

    # encerra um processo pelo PID enviando SIGTERM
    def kill(self, pid):
        try:
            psutil.Process(pid).terminate()
            return {"ok": True, "msg": f"Processo {pid} encerrado."}
        except psutil.NoSuchProcess:
            return {"ok": False, "msg": "PID não encontrado."}
        except psutil.AccessDenied:
            return {"ok": False, "msg": "Permissão negada."}


class PermissionManager:
    # lê as permissões de um arquivo ou pasta
    def get(self, path):
        if not os.path.exists(path):
            return {"error": "Caminho não encontrado."}

        info = os.stat(path)
        mode = stat.S_IMODE(info.st_mode)  # extrai só os bits de permissão

        # tenta pegar o nome do dono; se não achar, usa o número do uid
        try:
            owner = pwd.getpwuid(info.st_uid).pw_name
        except KeyError:
            owner = str(info.st_uid)

        # mesmo para o grupo
        try:
            group = grp.getgrgid(info.st_gid).gr_name
        except KeyError:
            group = str(info.st_gid)

        return {
            "octal": oct(mode),  # ex: 0o755
            "owner": owner,
            "group": group,
        }

    # altera as permissões com chmod (modo octal, ex: "755")
    def chmod(self, path, mode):
        try:
            os.chmod(path, int(mode, 8))  # converte string "755" para octal
            return {"ok": True, "msg": f"chmod {mode} aplicado."}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    # altera o dono com chown (ex: "usuario:grupo")
    def chown(self, path, owner):
        result = subprocess.run(["chown", owner, path], capture_output=True, text=True)

        if result.returncode == 0:
            return {"ok": True, "msg": f"chown {owner} aplicado."}

        return {"ok": False, "msg": result.stderr.strip()}