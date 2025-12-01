import requests
import config

def prom_query(query: str):
    """Prometheus Instant Query 헬퍼"""
    try:
        r = requests.get(
            f"{config.PROM_URL}/api/v1/query",
            params={"query": query},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            return []
        return data.get("data", {}).get("result", [])
    except Exception:
        return []

def get_node_stats():
    """각 노드의 CPU/메모리/디스크 사용률을 계산해서 리턴"""

    # CPU: 전체 코어, 사용중인 코어 비율
    cpu_total_q = "sum(rate(node_cpu_seconds_total[5m])) by (instance)"
    cpu_busy_q = "sum(rate(node_cpu_seconds_total{mode!='idle'}[5m])) by (instance)"

    mem_total_q = "node_memory_MemTotal_bytes"
    mem_free_q = "node_memory_MemAvailable_bytes"

    # 디스크는 / (root) 기준
    disk_total_q = "node_filesystem_size_bytes{mountpoint='/',fstype!~'tmpfs|overlay'}"
    disk_free_q = "node_filesystem_avail_bytes{mountpoint='/',fstype!~'tmpfs|overlay'}"

    cpu_total = {m["metric"]["instance"]: float(m["value"][1]) for m in prom_query(cpu_total_q)}
    cpu_busy = {m["metric"]["instance"]: float(m["value"][1]) for m in prom_query(cpu_busy_q)}
    mem_total = {m["metric"]["instance"]: float(m["value"][1]) for m in prom_query(mem_total_q)}
    mem_free = {m["metric"]["instance"]: float(m["value"][1]) for m in prom_query(mem_free_q)}
    disk_total = {m["metric"]["instance"]: float(m["value"][1]) for m in prom_query(disk_total_q)}
    disk_free = {m["metric"]["instance"]: float(m["value"][1]) for m in prom_query(disk_free_q)}

    results = []

    # 모든 인스턴스(노드)를 합쳐서 루프
    instances = (
        set(cpu_total.keys())
        | set(cpu_busy.keys())
        | set(mem_total.keys())
        | set(mem_free.keys())
        | set(disk_total.keys())
        | set(disk_free.keys())
    )

    for inst in instances:
        ct = cpu_total.get(inst, 0.0)
        cb = cpu_busy.get(inst, 0.0)
        mt = mem_total.get(inst, 0.0)
        mf = mem_free.get(inst, 0.0)
        dt = disk_total.get(inst, 0.0)
        df = disk_free.get(inst, 0.0)

        if ct <= 0 or mt <= 0 or dt <= 0:
            # 필요한 값이 없으면 스킵
            continue

        cpu_percent = round(cb / ct * 100, 2)
        mem_used = mt - mf
        disk_used = dt - df

        mem_percent = round(mem_used / mt * 100, 2)
        disk_percent = round(disk_used / dt * 100, 2)

        results.append({
            "node": inst.replace(":9100", ""),  # node exporter 기본 포트 제거
            "cpu_percent": cpu_percent,
            "mem_percent": mem_percent,
            "disk_percent": disk_percent,
            "mem_info": f"{round(mem_used/1024/1024/1024,2)}GB / {round(mt/1024/1024/1024,2)}GB",
            "disk_info": f"{round(disk_used/1024/1024/1024,2)}GB / {round(dt/1024/1024/1024,2)}GB",
        })

    return results

