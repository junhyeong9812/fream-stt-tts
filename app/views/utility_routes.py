from flask import Blueprint, request, jsonify, send_file, current_app
import os
import time

# 블루프린트 생성
utility_bp = Blueprint('utility', __name__)

# 생성된 오디오 파일 제공 API
@utility_bp.route('/audio/<path:filename>', methods=['GET'])
def get_audio(filename):
    temp_dir = current_app.config['TEMP_DIR']
    full_path = os.path.join(temp_dir, os.path.basename(filename))
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        return jsonify({'error': '파일을 찾을 수 없습니다'}), 404

# 임시 파일 정리를 위한 경로
@utility_bp.route('/cleanup', methods=['POST'])
def cleanup():
    filename = request.json.get('filename')
    if filename and os.path.exists(filename):
        try:
            os.unlink(filename)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'success': False})

# 주기적으로 오래된 임시 파일 정리 (1시간 이상 지난 파일)
@utility_bp.route('/cleanup/temp', methods=['POST'])
def cleanup_temp():
    temp_dir = current_app.config['TEMP_DIR']
    lifetime = current_app.config.get('TEMP_FILES_LIFETIME', 3600)  # 기본값 1시간
    now = time.time()
    count = 0
    
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            # 파일의 수정 시간이 지정된 시간 이상 지났는지 확인
            if now - os.path.getmtime(file_path) > lifetime:
                try:
                    os.unlink(file_path)
                    count += 1
                except Exception as e:
                    current_app.logger.error(f"임시 파일 정리 실패: {str(e)}")
    
    return jsonify({'success': True, 'deleted_files': count})