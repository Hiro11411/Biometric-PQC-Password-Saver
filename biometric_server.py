"""
Long-running stdio JSON server wrapping BiometricSystem, spawned by the Rust
side as a subprocess (see enigma-tauri/src-tauri/src/python_bridge.rs).

Protocol: newline-delimited JSON on stdin/stdout.
    -> {"id": 1, "cmd": "enroll", "params": {"user_id": 1}}
    <- {"id": 1, "ok": true, "result": {...}}
    <- {"id": 1, "ok": false, "error": "..."}

stdout carries ONLY protocol responses. Everything else (TensorFlow/OpenCV
logging, tracebacks) must go to stderr, or it corrupts the line-based
protocol Rust is parsing.
"""
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import sys
import json
import traceback

from biometric import BiometricSystem


def make_response(request_id, ok, result=None, error=None):
    return {"id": request_id, "ok": ok, "result": result, "error": error}


def handle_command(system, cmd, params):
    if cmd == "ping":
        return {"pong": True}

    if cmd == "enroll":
        user_id = params["user_id"]
        face_roi = system.capture_face_roi()
        path = system.biometric_encryption(face_roi, user_id)
        return {"path": path}

    if cmd == "verify":
        user_id = params["user_id"]
        face_roi = system.capture_face_roi()
        return system.biometric_decryption(face_roi, user_id)

    if cmd == "verify_emotion":
        target_emotion = params["target_emotion"]
        face_roi = system.capture_face_roi()
        emotion_dominant, confidence = system.emotional_analyzer(face_roi)
        matched = emotion_dominant == target_emotion and confidence > 0.5
        return {"matched": matched, "detected": emotion_dominant, "confidence": confidence}

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
