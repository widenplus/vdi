from flask import Blueprint, request, render_template, redirect, url_for, session
from db import verify_admin
from prometheus import get_node_stats

admin_bp = Blueprint("admin", __name__)

# (GET) 관리자 로그인 페이지
@admin_bp.route("/admin-login", methods=["GET"])
def admin_login_page():
    # 이미 로그인 상태면 대시보드로 보냄
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("admin_login.html")

# (POST) 관리자 로그인 처리
@admin_bp.route("/admin-login", methods=["POST"])
def admin_login():
    userid = request.form.get("userid")
    password = request.form.get("password")

    if not userid or not password:
        return render_template("admin_login.html", error="아이디와 비밀번호를 입력하세요.")

    if not verify_admin(userid, password):
        return render_template("admin_login.html", error="로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다.")

    # 세션 플래그 설정
    session["admin_logged_in"] = True
    session["admin_userid"] = userid

    return redirect(url_for("admin.admin_dashboard"))

# (GET) 관리자 대시보드
@admin_bp.route("/admin-dashboard", methods=["GET"])
def admin_dashboard():
    # 로그인 여부 체크
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login_page"))

    nodes = get_node_stats()

    # 노드 이름 기준 정렬
    try:
        nodes = sorted(nodes, key=lambda x: x.get("node", ""))
    except Exception:
        pass

    return render_template("admin_dashboard.html", nodes=nodes)

# (GET) 관리자 로그아웃
@admin_bp.route("/admin-logout", methods=["GET"])
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_userid", None)
    return "<script>alert('관리자 로그아웃되었습니다.'); location.href='/admin-login';</script>"

