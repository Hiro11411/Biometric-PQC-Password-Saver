"""
Manual, interactive test of the LIVE webcam + face recognition pipeline.
Unlike test_biometric_crypto.py (which uses a static face.jpg and only
checks the crypto math), this actually exercises your camera and the Haar
cascade detector in real time.

Run with: py -3.11 test_face_live.py

NOTE: the verification threshold currently has a known bug (flagged earlier)
-- 0.6 <= distance <= 0.8 instead of a simple distance < 0.8. Until that's
fixed, "verified: False" is EXPECTED even for your own face. Judge success
here by whether `distance` is small (under ~0.3-0.4), not by the verified
flag.
"""
import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import cv2
from biometric import BiometricSystem

TEST_USER_ID = 1


def step_1_capture_only(system):
    print("\n=== STEP 1: face detection only (no crypto) ===")
    print("Look at your webcam. Waiting up to 8 seconds for a face...")
    try:
        face_roi = system.capture_face_roi(timeout_seconds=8)
    except RuntimeError as e:
        print(f"FAILED: {e}")
        print("-> If 'Could not access webcam': check nothing else is using the camera,")
        print("   and that Windows camera privacy settings allow desktop apps access.")
        print("-> If 'No face detected': check lighting, distance from camera, and that")
        print("   haarcascade_frontalface_default.xml is present next to biometric.py.")
        return None

    print(f"OK: face detected, ROI shape = {face_roi.shape}")
    preview_path = "data/temp_faces/live_capture_preview.jpg"
    os.makedirs("data/temp_faces", exist_ok=True)
    cv2.imwrite(preview_path, face_roi)
    print(f"Saved a preview image to {preview_path} -- open it to confirm it's actually your face.")
    return face_roi


def step_2_enroll(system):
    print("\n=== STEP 2: enroll (encrypt) ===")
    print("Look at your webcam again for enrollment...")
    face_roi = system.capture_face_roi(timeout_seconds=8)
    path = system.biometric_encryption(face_roi, TEST_USER_ID)
    print(f"OK: enrolled, encrypted file written to {path}")


def step_3_verify(system):
    print("\n=== STEP 3: verify (decrypt + compare) ===")
    print("Look at your webcam again for verification...")
    face_roi = system.capture_face_roi(timeout_seconds=8)
    result = system.biometric_decryption(face_roi, TEST_USER_ID)
    print(f"Result: {result}")
    if result["distance"] is not None and result["distance"] < 0.4:
        print("-> distance is small: your face pipeline IS working correctly.")
        print("   'verified: False' here is the known threshold bug, not a real failure.")
    elif result["distance"] is not None:
        print("-> distance is large: something's off (bad lighting/angle mismatch between")
        print("   enrollment and verification, or a genuinely different face).")


if __name__ == "__main__":
    system = BiometricSystem()

    face_roi = step_1_capture_only(system)
    if face_roi is None:
        raise SystemExit(1)

    input("\nPress Enter to continue to enrollment...")
    step_2_enroll(system)

    input("\nPress Enter to continue to verification...")
    step_3_verify(system)

    # cleanup so re-running the script doesn't collide with a prior test enrollment
    enrolled_path = f"{system.enrolled_dir}/user_{TEST_USER_ID}_encrypted.npy"
    if os.path.exists(enrolled_path):
        os.remove(enrolled_path)
        print(f"\nCleaned up {enrolled_path}")



#depends on deep face own detector 