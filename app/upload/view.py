import time
from flask import request, jsonify, current_app
from flask_login import login_required
from . import upload_bp
import os, uuid, shutil
from diskcache import Cache


def get_cache():
    """取得 DiskCache 實例"""
    upload_root = current_app.config["UPLOAD_FOLDER"]
    cache_folder = os.path.join(upload_root, "update_cache")
    os.makedirs(cache_folder, exist_ok=True)
    return Cache(cache_folder)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    """檢查允許的檔案格式"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def cleanup_cache(cache_folder, cache):
    """刪除過期暫存檔"""
    cache.expire()  # 自動刪除過期 key
    for filename in list(cache):
        if filename.startswith("_"):  # 排除特殊 key
            continue
        expire_at = cache.expire_time(filename)
        if expire_at and expire_at < time.time():
            filepath = os.path.join(cache_folder, filename)
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"[WARN] 刪除暫存檔失敗: {filepath}, {e}")
            cache.pop(filename, None)


def increment_upload_count(cache, cache_folder, threshold=100):
    """每100次上傳清除快取一次"""
    count = cache.get("_upload_count", 0) + 1
    cache["_upload_count"] = count
    if count >= threshold:
        print(f"[INFO] 達到 {threshold} 次上傳，自動清理暫存檔")
        cleanup_cache(cache_folder, cache)
        cache["_upload_count"] = 0


@upload_bp.route("/", methods=["POST"])
# @login_required
def upload_file():
    """上傳暫存檔案"""
    cache = get_cache()
    upload_root = current_app.config["UPLOAD_FOLDER"]
    cache_folder = os.path.join(upload_root, "update_cache")

    file = request.files.get("file")
    print("[DEBUG] content_type:", request.content_type)
    print("[DEBUG] files:", request.files)
    print("[DEBUG] form:", request.form)
    if not file or file.filename == "":
        return jsonify({"error": "未選擇檔案"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支援的檔案格式"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(cache_folder, new_filename)
    file.save(save_path)

    cache.set(new_filename, {"status": "cached"}, expire=3600)
    increment_upload_count(cache, cache_folder)

    return jsonify({"filename": new_filename})


def save_file(filename):
    """把暫存檔移到正式資料夾"""
    cache = get_cache()
    upload_root = current_app.config["UPLOAD_FOLDER"]
    cache_folder = os.path.join(upload_root, "update_cache")

    cached_path = os.path.join(cache_folder, filename)
    final_path = os.path.join(upload_root, filename)

    if not os.path.exists(cached_path):
        print(f"[WARN] 暫存檔不存在: {filename}")
        return None

    try:
        shutil.move(cached_path, final_path)
        cache.pop(filename, None)
        print(f"[INFO] 已移動到正式目錄: {final_path}")
        return final_path
    except Exception as e:
        print(f"[ERROR] 移動失敗: {e}")
        return None

def del_file(filename):
    """刪除正式資料夾裡的檔案"""
    upload_root = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_root, filename)
    try:
        os.remove(filepath)
    except Exception as e:
        print(f"[WARN] 刪除暫存檔失敗: {filepath}, {e}")



