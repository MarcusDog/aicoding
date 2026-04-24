from flask import jsonify


def success_response(data=None, message: str = "success", code: int = 200):
    payload = {"success": True, "message": message, "data": data}
    return jsonify(payload), code


def error_response(message: str = "error", code: int = 400, data=None):
    payload = {"success": False, "message": message, "data": data}
    return jsonify(payload), code
