"""
Live visual accuracy panel for testing biometric_decryption in real time.

Opens a window showing your webcam feed with a bounding box around any
detected face and a running accuracy/confidence readout. The accuracy number
comes from periodically running the REAL enroll/verify pipeline (Kyber
decapsulation + AES-GCM decrypt + DeepFace embedding compare) -- this is not
a simulation, it's the actual biometric.py code running live.

Controls:
  e - enroll the currently detected face as the reference for this session
  q - quit

Run with: py -3.11 test_face_accuracy_panel.py
"""
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import ctypes
import sys
import time
import cv2
from biometric import BiometricSystem

MB_ICONERROR = 0x10


def show_spoof_alert():
    """Native Windows message box -- no extra dependency needed, ctypes calls
    directly into user32.dll."""
    ctypes.windll.user32.MessageBoxW(
        0,
        "A photo or screen was detected instead of a live face.\nThe program will now close.",
        "Enigma - Spoof Detected",
        MB_ICONERROR,
    )

TEST_USER_ID = 1
VERIFY_EVERY_N_FRAMES = 20      # throttle -- DeepFace inference is too slow to run every frame
DEEPFACE_MATCH_THRESHOLD = 0.8  # DeepFace's own recommended Facenet + euclidean_l2 threshold

TEXT_COLOR = (60, 220, 60)
BOX_COLOR = (60, 220, 60)


def accuracy_percent(distance):
    """Maps a Euclidean distance to an intuitive 0-100% readout, anchored to
    DeepFace's own recommended match threshold (0.8) -- NOT the app's current
    0.6-0.8 threshold band, which is a separate known bug. This is purely a
    visualization to help you judge match quality while testing."""
    if distance is None:
        return None
    pct = (1 - distance / DEEPFACE_MATCH_THRESHOLD) * 100
    return max(0.0, min(100.0, pct))


def main():
    system = BiometricSystem()
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW) #DSHOW avoids MSMF frame-grab failures on some Windows webcams
    if not video.isOpened():
        raise RuntimeError("Could not access webcam")

    enrolled_path = f"{system.enrolled_dir}/user_{TEST_USER_ID}_encrypted.npy"
    enrolled = os.path.exists(enrolled_path)

    last_distance = None
    last_accuracy = None
    last_verified = None
    last_spoof = False
    frame_count = 0

    print("Controls: [e] enroll current face   [q] quit")
    print(f"user_id={TEST_USER_ID} " + ("has enrolled data -- verifying against it." if enrolled
                                         else "has no enrolled data yet -- press 'e' to enroll first."))

    terminated_due_to_spoof = False
    consecutive_failures = 0
    try:
        while True:
            ret, frame = video.read()
            if not ret:
                consecutive_failures += 1
                if consecutive_failures > 50:
                    raise RuntimeError("Webcam opened but repeatedly failed to grab frames")
                time.sleep(0.05) #avoid a tight spin loop while waiting for a real frame
                continue
            consecutive_failures = 0

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = system.face_cascade.detectMultiScale(gray, 1.3, 5)

            face_present = len(faces) > 0
            if face_present:
                x, y, w, h = faces[0]
                cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, 2)

                frame_count += 1
                if enrolled and frame_count % VERIFY_EVERY_N_FRAMES == 0:
                    #Pass the FULL frame, not a tight crop -- let DeepFace's own
                    #detector do proper face detection + alignment. A tight,
                    #jittery Haar-cascade crop was producing wildly inconsistent
                    #embeddings (and confusing the anti-spoofing model).
                    result = system.biometric_decryption(frame, TEST_USER_ID)
                    last_distance = result["distance"]
                    last_verified = result["verified"]
                    last_spoof = result.get("spoof_detected", False)
                    last_accuracy = accuracy_percent(last_distance)
                    if last_spoof:
                        print("SPOOF DETECTED -- rejected as a photo/screen, not a live face. Terminating.")
                        terminated_due_to_spoof = True
                        break
                    else:
                        print(f"Accuracy: {last_accuracy:5.1f}%   Distance: {last_distance:.4f}   "
                              f"verified flag: {last_verified}")

            frames_until_update = VERIFY_EVERY_N_FRAMES - (frame_count % VERIFY_EVERY_N_FRAMES)

            status_lines = [f"Frame: {frame_count}"]
            if not enrolled:
                status_lines.append("NOT ENROLLED -- press 'e'")
            elif last_spoof:
                status_lines.append("SPOOF DETECTED -- rejected as photo/screen")
            elif last_accuracy is None:
                status_lines.append("Detecting...")
            else:
                status_lines.append(f"Accuracy: {last_accuracy:5.1f}%   (next update in {frames_until_update})")
                status_lines.append(f"Distance: {last_distance:.4f}")
                status_lines.append(f"App 'verified' flag: {last_verified} (threshold bug -- ignore for now)")

            for i, text in enumerate(status_lines):
                cv2.putText(frame, text, (10, 30 + i * 28), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, TEXT_COLOR, 2)

            cv2.imshow("Enigma - Live Accuracy Test", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('e') and face_present:
                system.biometric_encryption(frame, TEST_USER_ID)
                enrolled = True
                last_distance = None
                last_accuracy = None
                last_verified = None
                last_spoof = False
                frame_count = 0
                print("Enrolled current face as the reference.")
    finally:
        video.release()
        cv2.destroyAllWindows()

    if terminated_due_to_spoof:
        show_spoof_alert()
        sys.exit(1)


if __name__ == "__main__":
    main()
