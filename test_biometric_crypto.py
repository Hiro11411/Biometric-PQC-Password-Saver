"""
Correctness tests for the Kyber512 + AES-256-GCM encryption pipeline in
biometric.py. These prove the pipeline is functionally correct and that its
tamper-detection actually works -- they do NOT and cannot prove Kyber's
quantum-resistance itself, which rests on published cryptanalysis and NIST's
standardization (FIPS 203), not on anything testable at this level.

Run with: py -3.11 -m pytest test_biometric_crypto.py -v
"""
import os

import cv2
import numpy as np
import pytest

from biometric import BiometricSystem
from kyber_py.kyber import Kyber512

FACE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "face.jpg")
TEST_USER_ID = 999999  # unlikely to collide with a real enrolled user


@pytest.fixture(scope="module")
def system():
    # anti_spoofing=False here on purpose: these tests use a canned static
    # photo to exercise the crypto pipeline deterministically, not to
    # simulate a live face -- the real production default is
    # anti_spoofing=True (see test_spoof_detected_on_static_photo below,
    # which uses the real default specifically to confirm that).
    return BiometricSystem(anti_spoofing=False)


@pytest.fixture(scope="module")
def face_image():
    img = cv2.imread(FACE_IMAGE_PATH)
    if img is None:
        pytest.skip(f"Could not load test face image at {FACE_IMAGE_PATH}")
    return img


@pytest.fixture(autouse=True)
def cleanup_enrollment(system):
    yield
    enrolled_path = f"{system.enrolled_dir}/user_{TEST_USER_ID}_encrypted.npy"
    if os.path.exists(enrolled_path):
        os.remove(enrolled_path)


def test_round_trip_verifies_same_face(system, face_image):
    """Encrypting then decrypting the SAME image should recover the exact
    original embedding and pass the verification threshold. FaceNet is
    deterministic for a fixed input, so the distance should be ~0, not just
    "under the 0.8 threshold" -- that distinguishes real correctness from a
    coincidental pass."""
    system.biometric_encryption(face_image, TEST_USER_ID)
    result = system.biometric_decryption(face_image, TEST_USER_ID)

    assert result["verified"] is True
    assert result["distance"] < 0.01


def test_spoof_detected_on_static_photo(face_image):
    """Confirms the REAL production default (anti_spoofing=True) actually
    rejects a static photo as a liveness failure. This is the automated
    counterpart to manually testing with a phone photo -- a static image
    file is functionally the same kind of presentation attack."""
    real_system = BiometricSystem()  # anti_spoofing=True, the real default
    with pytest.raises(ValueError, match="Spoof detected"):
        real_system.biometric_encryption(face_image, TEST_USER_ID)


def test_missing_enrollment_fails_cleanly(system, face_image):
    """Verifying against a user_id that was never enrolled must return
    verified=False, not raise."""
    result = system.biometric_decryption(face_image, user_id=TEST_USER_ID)
    assert result == {"verified": False, "distance": None, "spoof_detected": False}


def test_tampered_auth_tag_is_rejected(system, face_image):
    """Corrupting the GCM auth tag must cause decryption to fail loudly.
    This is the single most important negative test for an AEAD scheme --
    if this doesn't raise, tamper detection isn't actually enforced."""
    system.biometric_encryption(face_image, TEST_USER_ID)

    enc_path = f"{system.enrolled_dir}/user_{TEST_USER_ID}_encrypted.npy"
    data = np.load(enc_path, allow_pickle=True).item()
    data["tag"] = bytes(len(data["tag"]))  # zero out the tag
    np.save(enc_path, data, allow_pickle=True)

    with pytest.raises(ValueError):
        system.biometric_decryption(face_image, TEST_USER_ID)


def test_tampered_ciphertext_is_rejected(system, face_image):
    """Flipping a bit in the encrypted embedding must also fail verification
    instead of silently decrypting to garbage."""
    system.biometric_encryption(face_image, TEST_USER_ID)

    enc_path = f"{system.enrolled_dir}/user_{TEST_USER_ID}_encrypted.npy"
    data = np.load(enc_path, allow_pickle=True).item()
    corrupted = bytearray(data["encrypted"])
    corrupted[0] ^= 0xFF
    data["encrypted"] = bytes(corrupted)
    np.save(enc_path, data, allow_pickle=True)

    with pytest.raises(ValueError):
        system.biometric_decryption(face_image, TEST_USER_ID)


def test_wrong_secret_key_cannot_decapsulate():
    """Kyber's own guarantee, tested directly: a secret key from a DIFFERENT
    keypair must not recover the correct shared secret from someone else's
    ciphertext. (Kyber uses implicit rejection -- a wrong key silently
    returns a different, deterministic-looking secret rather than raising,
    so we assert inequality rather than expecting an exception.)"""
    pk_a, _ = Kyber512.keygen()
    _, sk_b = Kyber512.keygen()

    shared_secret_a, ciphertext = Kyber512.encaps(pk_a)
    recovered_with_wrong_key = Kyber512.decaps(sk_b, ciphertext)

    assert recovered_with_wrong_key != shared_secret_a


def test_kyber512_self_consistency_many_trials():
    """Kyber512 keygen/encaps/decaps must agree with itself across many
    independent trials. This is a correctness proxy, not a substitute for
    official NIST KAT vectors (see test_kyber512_nist_kat below) -- but it
    does catch gross implementation errors (e.g. a broken decoding step that
    only fails for certain random polynomials)."""
    for _ in range(20):
        pk, sk = Kyber512.keygen()
        shared_secret, ciphertext = Kyber512.encaps(pk)
        recovered = Kyber512.decaps(sk, ciphertext)
        assert recovered == shared_secret


@pytest.mark.skip(
    reason=(
        "kyber_py's public Kyber512.keygen()/encaps() API does not expose "
        "deterministic seeding, so official NIST ML-KEM-512 KAT vectors "
        "(fixed seed -> expected pk/sk/ciphertext/shared_secret bytes) "
        "can't be wired up without reaching into the library's internal DRBG "
        "module. To do this properly: pull the official vectors from "
        "https://github.com/post-quantum-cryptography/KAT and check whether "
        "kyber_py's own upstream repo (not the installed package) bundles a "
        "test suite that already seeds kyber_py.drbg.aes256_ctr_drbg for "
        "exactly this purpose."
    )
)
def test_kyber512_nist_kat():
    raise NotImplementedError
