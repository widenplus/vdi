from flask import Blueprint, request
from k8s import delete_user_pod

desktop_bp = Blueprint("desktop", __name__)

# (POST) 데스크탑 삭제 요청 (관리자/도구용 API)
@desktop_bp.route("/delete-desktop", methods=["POST"])
def delete_desktop():
    username = request.form.get("username")

    if not username:
        return "<script>alert('username 이 필요합니다.'); history.back();</script>"

    delete_user_pod(username)
    return "<script>alert('데스크탑 삭제 완료'); history.back();</script>"

