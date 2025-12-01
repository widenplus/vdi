from flask import Blueprint, request, session, render_template
from db import verify_user
from k8s import ensure_namespace, calc_nodeport, pod_exists, create_user_pod, delete_user_pod
import config

user_bp = Blueprint("user", __name__)

@user_bp.route("/", methods=["GET"])
def login_page():
    return render_template("user_login.html")

@user_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "<script>alert('아이디와 비밀번호를 입력하세요.'); history.back();</script>"

    user = verify_user(username, password)

    if not user:
        return "<script>alert('로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다.'); history.back();</script>"

    session["username"] = username

    ensure_namespace()
    port = calc_nodeport(username)

    if pod_exists(username):
        delete_user_pod(username)

    create_user_pod(username, port, password)

    url = f"http://{config.NODE_IP}:{port}"
    return f"<script>location.href='{url}';</script>"


@user_bp.route("/logout", methods=["GET"])
def logout():
    username = session.get("username")

    if username:
        delete_user_pod(username)

    session.clear()
    return "<script>alert('로그아웃 되었습니다. 데스크탑이 삭제됩니다.'); location.href='/';</script>"

