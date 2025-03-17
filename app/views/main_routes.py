from flask import Blueprint, render_template, current_app

# 블루프린트 생성
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    메인 페이지를 렌더링합니다.
    """
    return render_template('main.html')