"""
Long-running stdio JSON server wrapping BiometricSystem, spawned by the Rust
side as a subprocess (see enigma-tauri/src-tauri/src/python_bridge.rs).

Protocol: newline-delimited JSON on stdin/stdout.
    -> {"id": 1, "cmd": "enroll", "params": {"user_id": 1, "image_base64": "..."}}
    <- {"id": 1, "ok": true, "result": {...}}
    <- {"id": 1, "ok": false, "error": "..."}

The frontend captures frames via the browser's own camera access (getUserMedia)
and sends a single still frame per request as base64 JPEG -- this process no
longer opens the webcam itself for real app requests (capture_face_roi()
still exists on BiometricSystem for the standalone test scripts only).

stdout carries ONLY protocol responses. Everything else (TensorFlow/OpenCV
logging, tracebacks) must go to stderr, or it corrupts the line-based
protocol Rust is parsing.
"""
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import sys
import json
import base64
import traceback

import numpy as np
import cv2

from biometric import BiometricSystem


def make_response(request_id, ok, result=None, error=None):
    return {"id": request_id, "ok": ok, "result": result, "error": error}


def decode_image(image_base64):
    """Decodes a base64 JPEG (as sent by the frontend's canvas capture) into
    the same BGR numpy array shape OpenCV/DeepFace expect from a live frame."""
    raw_bytes = base64.b64decode(image_base64)
    array = np.frombuffer(raw_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode image_base64 -- not a valid image")
    return frame


def save_password(system, params):
    """Stub -- vault persistence (SQLite insert into vault_entries) to be filled in separately."""
    raise NotImplementedError("save_password is not implemented yet")


def get_passwords(system, params):
    """Stub -- vault persistence (SQLite select from vault_entries) to be filled in separately."""
    raise NotImplementedError("get_passwords is not implemented yet")


def update_password(system, params):
    """Stub -- vault persistence (SQLite update on vault_entries) to be filled in separately."""
    raise NotImplementedError("update_password is not implemented yet")


def delete_password(system, params):
    """Stub -- vault persistence (SQLite delete from vault_entries) to be filled in separately."""
    raise NotImplementedError("delete_password is not implemented yet")


def handle_command(system, cmd, params):
    if cmd == "ping":
        return {"pong": True}

    if cmd == "enroll":
        user_id = params["user_id"]
        frame = decode_image(params["image_base64"])
        path = system.biometric_encryption(frame, user_id)
        return {"path": path}

    if cmd == "verify":
        user_id = params["user_id"]
        frame = decode_image(params["image_base64"])
        return system.biometric_decryption(frame, user_id)

    if cmd == "verify_emotion":
        target_emotion = params["target_emotion"]
        frame = decode_image(params["image_base64"])
        emotion_dominant, confidence = system.emotional_analyzer(frame)
        matched = emotion_dominant == target_emotion and confidence > 0.5
        return {"matched": matched, "detected": emotion_dominant, "confidence": confidence}

    if cmd == "save_password":
        return save_password(system, params)

    if cmd == "get_passwords":
        return get_passwords(system, params)

    if cmd == "update_password":
        return update_password(system, params)

    if cmd == "delete_password":
        return delete_password(system, params)

    raise ValueError(f"Unknown command: {cmd}")


def main():
    system = BiometricSystem()

    # Announce readiness on stdout so Rust knows the (slow) model-loading
    # startup has finished before it sends the first real request.
    print(json.dumps(make_response(0, True, result={"status": "ready"})), flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            print(json.dumps(make_response(None, False, error=f"bad json: {e}")), flush=True)
            continue

        request_id = request.get("id")
        cmd = request.get("cmd")
        params = request.get("params", {})

        try:
            result = handle_command(system, cmd, params)
            response = make_response(request_id, True, result=result)
        except Exception as e:
            traceback.print_exc(file=sys.stderr)  # full traceback -> stderr, never stdout
            response = make_response(request_id, False, error=str(e))

        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
