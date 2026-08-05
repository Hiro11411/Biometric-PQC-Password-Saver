# Enigma — Project Status Summary

Written for a fresh Claude session (or any new collaborator) to get oriented quickly. This is a personal research project — a biometric password manager secured with post-quantum cryptography.

## What this project actually is

A desktop password manager where **your face is the login**, not a master password. Two halves:

1. **Python backend** — face recognition + encryption logic. Lives at `C:\Users\ganst\Desktop\biometric pws\Biometric-PQC-Password-Saver\`
2. **Tauri desktop frontend** — React UI + Rust shell. Lives at `C:\Users\ganst\Desktop\biometric pws\enigma-tauri\` (sibling folder to the Python backend, both under `biometric pws\`)

**Correction (2026-07-27):** an earlier version of this doc said the frontend lived at `C:\Users\ganst\Desktop\pws website\enigma-tauri\`. That was wrong — that folder is a **completely separate advertising website** for the software, unrelated to the actual app, despite the confusingly identical `enigma-tauri` name. The real frontend was rebuilt from scratch at the path above. Do not confuse the two; if you find yourself reading files under `pws website\`, you are in the wrong project.

## Architecture

```
┌─────────────────────────┐         stdio JSON          ┌──────────────────────────┐
│   enigma-tauri (Rust)    │ ───────────────────────────▶│  biometric_server.py     │
│   src-tauri/src/main.rs  │◀─────────────────────────── │  (spawned subprocess)    │
│   + python_bridge.rs     │                              │  wraps BiometricSystem   │
└───────────┬──────────────┘                              └──────────────────────────┘
            │ Tauri IPC (invoke)
┌───────────▼──────────────┐
│  React frontend (webview)│
│  Login/Signup/Vault      │
│  camera via getUserMedia │
└───────────────────────────┘
```

- The **frontend** captures webcam frames itself (browser `getUserMedia`, no Python/Tauri involvement for *display*) and sends a single still frame as base64 JPEG when the user takes an action (scan/enroll).
- **Rust** (`main.rs`) exposes three Tauri commands — `enroll_face`, `verify_face`, `verify_emotion` — each forwarding to Python via `python_bridge.rs`.
- **`python_bridge.rs`** spawns `py -3.11 biometric_server.py` once at app startup, holds its stdin/stdout pipes behind a `Mutex` (calls are serialized — one request/response round trip at a time, no concurrent request matching needed).
- **`biometric_server.py`** is a long-running loop reading newline-delimited JSON from stdin, dispatching to `BiometricSystem` methods, writing JSON responses to stdout. stdout carries *only* protocol messages — TensorFlow/OpenCV logging is forced to stderr, or it'd corrupt the line-based protocol.
- **`biometric.py`** (`BiometricSystem` class) has the actual crypto/recognition logic.

## The crypto pipeline (biometric.py)

1. Face image (from frontend now, not Python's own webcam capture for real app use) → DeepFace/FaceNet → 512-D embedding
2. Kyber-512 (`kyber-py` library) generates a keypair, encapsulates a random 32-byte shared secret
3. SHA-256 derives an AES key from that shared secret
4. AES-256-GCM encrypts the embedding, with a fresh nonce per encryption
5. Saved to disk: `{encrypted, tag, nonce, ciphertext, kyber_secret_key}` as a `.npy` file per user

**Anti-spoofing is real and working** — DeepFace's built-in Fasnet liveness model (`anti_spoofing=True`), confirmed to correctly reject photos/screens shown to the camera (tested against an actual phone photo).

## Known bugs / unfinished — be honest about these, don't assume they're fixed

1. 🔴 **The verification threshold is still wrong**: `biometric_decryption` uses `0.6 <= distance <= 0.8` (a band with a minimum) instead of `distance < 0.8` (DeepFace's own recommended threshold for Facenet+euclidean_l2). This means a genuine match can still fail. **Never silently "fixed" — the user has been asked multiple times whether to change this and hasn't confirmed yet.** It's a security-relevant parameter, not mine to change unilaterally.
2. 🔴 **The Kyber secret key is stored in the same file as the ciphertext it decrypts** (`kyber_secret_key` sits right in the `data_to_save` dict next to `encrypted`/`ciphertext`). Anyone with file access can decrypt everything — this is the single biggest real security gap. Discussed fix: wrap the secret key with Windows DPAPI before it touches disk. **Not implemented yet.**
3. `db.py` has a schema skeleton now (`get_connection`, `create_vault_table`, and empty `insert_entry`/`get_all_entries`/`update_entry`/`delete_entry` stubs marked `# TODO: implement`) but no real query logic yet. `vault_entries` columns: `service`/`username`/`encrypted_password`/`nonce`/`tag`/`user_id`. One master Kyber keypair per user (not one per password entry), SQLite (not PostgreSQL — single-user/local, a server model is overkill).
4. `pw_encryption`/`pw_decryption` in `biometric.py` are empty `pass` stubs.
5. `Signup.tsx` needs a numeric `user_id` for `biometric.py`'s API but there's no real user table yet — currently uses a **deterministic hash of the username as a placeholder** (clearly commented in the code as temporary), not a real assigned ID.
6. Password-vault Tauri commands exist as stubs now (`save_password`/`get_passwords`/`update_password`/`delete_password` in `main.rs`, dispatched in `biometric_server.py` to Python functions that `raise NotImplementedError`) — `Vault.tsx` calls them for real via `invoke()`, catches the expected failure, and falls back to local mock data so the screen still renders end-to-end. Real persistence (wiring these into `db.py`) not implemented yet.
7. Not yet packaged for distribution — Rust spawns `py -3.11 biometric_server.py` directly, requiring Python installed on whatever machine runs it. PyInstaller bundling was discussed as a later step, not started.

## Design decisions worth knowing the "why" of

- **Full frame, not a cropped face image, gets passed to DeepFace.** Originally `capture_face_roi()` pre-cropped tightly to a Haar cascade box before handing it to DeepFace — this caused wildly inconsistent embeddings (distances jumping 2–9 for the same live face) AND confused the anti-spoofing model (trained on natural frames, not zoomed crops). Fixed by handing DeepFace the full frame and letting its own detector do proper alignment; Haar cascade is now only used as a cheap "is a face roughly present" gate.
- **SQLite over PostgreSQL** for the vault: this is a single-user, single-machine tool, not a networked multi-client app. A Postgres server process is unnecessary attack surface (an open port, credentials to manage) for something that just needs one local file.
- **One master key per user, not one Kyber keypair per password entry** — avoids multiplying the "where do we protect this secret key" problem across every saved password.
- **Camera capture moved from Python to the browser** (`getUserMedia` in the frontend) specifically so the live feed renders inside the actual Tauri app window, not as a separate native `cv2.imshow()` popup. Python no longer opens the webcam for real app requests — it only processes already-captured still frames sent from the frontend. (The standalone test scripts below still use Python's own webcam capture, since they're meant to test outside the app.)

## Standalone test scripts (Python side, not part of the app itself)

- `test_biometric_crypto.py` — pytest suite: round-trip encryption, tamper-detection (wrong tag/ciphertext), wrong-key rejection, Kyber self-consistency, and a dedicated spoof-detection test. Run: `py -3.11 -m pytest test_biometric_crypto.py -v`
- `test_face_live.py` — guided step-by-step manual test (capture → enroll → verify) using your real webcam.
- `test_face_accuracy_panel.py` — live OpenCV window showing your webcam feed with a real-time accuracy/distance readout and hard spoof-detection (shows a native Windows error dialog and terminates immediately if a spoof is detected). This one legitimately uses `cv2.imshow()` since it's a standalone diagnostic tool, not part of the actual app UI.

## Environment specifics worth knowing

- Python 3.11 installed via winget, invoked as `py -3.11` (not `python`/`python3` — those are Windows Store stub aliases that don't actually work)
- `opencv-python` is pinned `<5` — OpenCV 5.0 removed `cv2.CascadeClassifier` entirely (replaced by a DNN-based detector), which this codebase's Haar cascade usage depends on
- Full dependency list in `requirements.txt`: opencv-python<5, deepface, numpy, kyber-py, pycryptodome, tf-keras (needed alongside Keras 3 for DeepFace's RetinaFace backend), torch (needed for DeepFace's anti-spoofing model)
- Windows 10, PowerShell — the Bash tool available in this environment resets its working directory between tool calls (a sandboxing quirk, not a real error) — `cd` + command must be chained in one call when working outside the primary project folder
