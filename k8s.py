import subprocess
import config

def ensure_namespace():
    """gui 전용 네임스페이스가 없으면 생성"""
    subprocess.run(
        ["kubectl", "create", "namespace", config.NAMESPACE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def pod_exists(username: str) -> bool:
    """해당 사용자의 GUI Pod 존재 여부 확인"""
    name = f"gui-{username}"
    result = subprocess.run(
        ["kubectl", "get", "pod", name, "-n", config.NAMESPACE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0

def calc_nodeport(username: str) -> int:
    """사용자별 고정 NodePort 계산 (충돌 최소화)"""
    # BASE_NODEPORT ~ BASE_NODEPORT+499 사이로 분배
    return config.BASE_NODEPORT + (abs(hash(username)) % 500)

def create_user_pod(username: str, node_port: int, password: str):
    image = "dorowu/ubuntu-desktop-lxde-vnc"

    yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: gui-{username}
  namespace: {config.NAMESPACE}
  labels:
    user: {username}
spec:
  containers:
    - name: desktop
      image: {image}
      env:
        - name: VNC_PW
          value: "{password}"
      ports:
        - containerPort: 80
        - containerPort: 6081
  restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: gui-{username}-svc
  namespace: {config.NAMESPACE}
spec:
  type: NodePort
  selector:
    user: {username}
  ports:
    - name: http
      port: 80
      targetPort: 80
      nodePort: {node_port}
"""
    subprocess.run(
        ["kubectl", "apply", "-n", config.NAMESPACE, "-f", "-"],
        input=yaml.encode()
    )


def delete_user_pod(username: str):
    """해당 사용자의 Pod + Service 삭제"""
    pod_name = f"gui-{username}"
    svc_name = f"gui-{username}-svc"

    subprocess.run(
        ["kubectl", "delete", "pod", pod_name, "-n", config.NAMESPACE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["kubectl", "delete", "svc", svc_name, "-n", config.NAMESPACE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

