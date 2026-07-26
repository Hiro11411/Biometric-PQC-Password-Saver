import time
import cv2
from deepface import DeepFace
from deepface.modules.exceptions import SpoofDetected
import numpy as np
from kyber_py.kyber import Kyber512
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#cascade is used for speed, recognition of the different prompts
#haar features used, check notes
class BiometricSystem:
    def __init__(self, anti_spoofing=True):
        """
        anti_spoofing=True (the secure default) rejects photos/screens shown
        to the camera instead of a live face. Only disable this for testing
        against canned/static images that aren't meant to simulate liveness --
        never disable it for real enrollment/verification.
        """
        self.anti_spoofing = anti_spoofing

        cascade_path = os.path.join(BASE_DIR, 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(cascade_path) #calling self, to later access it in the future

        #file directory section
        self.enrolled_dir = os.path.join(BASE_DIR, "data", "enrolled_faces")
        self.temp_dir = os.path.join(BASE_DIR, "data", "temp_faces")
        os.makedirs(self.enrolled_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def capture_face_roi(self, timeout_seconds=8):
        """
        Opens the webcam and waits until a face is roughly present in view,
        then returns the FULL captured frame -- not a tight pre-crop.

        Haar cascade boxes jitter noticeably frame-to-frame (no consistent
        eye-level alignment), so pre-cropping tightly to that box was handing
        DeepFace a differently-framed, unaligned face patch on every call.
        That made FaceNet embeddings unreliable (wildly varying distances
        for the same live face) and also fed the anti-spoofing model an
        unnatural, context-free image. DeepFace's own detector (with
        align=True by default) does proper face detection + alignment when
        given the full frame -- Haar cascade here is only a cheap gate to
        decide "yes, a face is roughly in view, proceed."
        """
        video = cv2.VideoCapture(0, cv2.CAP_DSHOW) #DSHOW avoids MSMF frame-grab failures on some Windows webcams
        if not video.isOpened():
            raise RuntimeError("Could not access webcam")

        try:
            start = time.time()
            consecutive_failures = 0
            while time.time() - start < timeout_seconds:
                ret, frame = video.read()
                if not ret:
                    consecutive_failures += 1
                    if consecutive_failures > 50:
                        raise RuntimeError("Webcam opened but repeatedly failed to grab frames")
                    time.sleep(0.05) #avoid a tight spin loop while waiting for a real frame
                    continue
                consecutive_failures = 0

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #START IN GRAY COLOR, using BGR FORMAT NOT RGB
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                if len(faces) > 0:
                    return frame #hand DeepFace's own detector the full frame for proper alignment

            raise RuntimeError("No face detected within timeout")
        finally:
            video.release()

    def id_input(self): #func for now only, change in the future
        """
        Tracks all of the id's and inputs, if invalid returns invalid and retrys
        """
        while True: #while function automatically restarts
            try:
                user_id = int(input("Enter Your ID: ")) #must be an integer value or flag as false
                return user_id
            except ValueError:
                print("This user_id is invalid, please try again !") #returns val error


    def emotional_analyzer(self, face_roi):  #add threshold
        """
        Tracks emotion based off different percentages in the confidence of expression the person is making, provides a threshold so more stablizied results
        in if the faces they are making are correct or not.
        """
        #analyzation of emotion
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
        emotion_dominant = result[0]['dominant_emotion'] #returns the dominant emotion, retrived FROM THE DICT of emotions, always first column
        emotion = result[0]['emotion'] #returns the emotions, and all the values of emotions
        confidence = emotion[emotion_dominant] / 100.0 #emotional confidence indicator as a percentage
        print(confidence, emotion, emotion_dominant)
        return emotion_dominant, confidence #parameter passing here

    def biometric_encryption(self, face_roi, user_id):
        """
        First time capturing the your face, saving the data for future use of analysis.
        REMB SHOULD ONLY BE RUN ONCE, FIX IN THE FUTURE
        """

        #===============================================================================================================================================================================================================
        #facial recognition part
        #===============================================================================================================================================================================================================
        temp_path = f"{self.temp_dir}/user_{user_id}.jpg" #save data

        cv2.imwrite(temp_path, face_roi)

        #===============================================================================================================================================================================================================
        #Kyber Encryption
        #===============================================================================================================================================================================================================

        #extract embedding, specific model
        try:
            embedding = DeepFace.represent(
                    img_path = temp_path,
                    model_name="Facenet",
                    anti_spoofing=self.anti_spoofing, #reject photos/screens shown to the camera during enrollment
                )
        except SpoofDetected:
            os.remove(temp_path)
            raise ValueError("Spoof detected during enrollment -- use a live face, not a photo or screen")

        embedded = embedding[0]['embedding'] #list of embedded values, convert in bytes

        embedded_bytes = np.array(embedded).tobytes() #encoding part

        pk, sk = Kyber512.keygen() #public and seret key gen

        shared_secret, ciphertext = Kyber512.encaps(pk) #encaps are returning them in the wrong order, shared_secret first cipher text next

        #===============================================================================================================================================================================================================
        #SHA Encryption + AES Encryption,  #sha 256 Encryption -> converts to AES key format, end goal Shared_secret == secret
        #===============================================================================================================================================================================================================

        new_SHA = SHA256.new()

        new_SHA.update(shared_secret) #add shared secret to the SHA key

        aes_key_raw = new_SHA.digest() #convert into bytes

        #encrypt with AES, nonce number so that each combination is different

        nonce = get_random_bytes(12)  #completely different thing from SHA

        cipher = AES.new(aes_key_raw, AES.MODE_GCM, nonce=nonce) #combination of all 3

        encrypted_embedding, tag = cipher.encrypt_and_digest(embedded_bytes) #tamper detector using tag, so attackers can't change your data

        #save encrypted version and set it into a path
        encrypted_path = f"{self.enrolled_dir}/user_{user_id}_encrypted.npy"

        data_to_save = {
            'encrypted': encrypted_embedding,
            'tag': tag,
            'nonce': nonce,
            'ciphertext': ciphertext,
            'kyber_secret_key': sk
        }

        np.save(encrypted_path, data_to_save, allow_pickle=True) #addition to dictionary
        #used to load the data later

        print(f"Face Enrolled for {user_id}!") #enrolled msg

        os.remove(temp_path) #remove path so cant trace

        return encrypted_path #for future use and calling

    def biometric_decryption(self, face_roi, user_id):
        """
        Compares your first and tries to verify your face.
        """

        #Comparison of Originally Encrypted Path
        enrolled_encrypted_path = f"{self.enrolled_dir}/user_{user_id}_encrypted.npy"

        if not os.path.exists(enrolled_encrypted_path):
            print("No enrolled data for this user") #link this back to your front end
            return {"verified": False, "distance": None, "spoof_detected": False}

        temp_path = f"{self.temp_dir}/temp_{user_id}.png" #temp path for access
        cv2.imwrite(temp_path, face_roi)

        try:
            embedding = DeepFace.represent(
                img_path=temp_path,
                model_name="Facenet",
                anti_spoofing=self.anti_spoofing, #reject photos/screens shown to the camera during verification
            )
        except SpoofDetected:
            os.remove(temp_path)
            print("Spoof detected -- rejecting a photo/screen presented instead of a live face")
            return {"verified": False, "distance": None, "spoof_detected": True}

        current_embedding = embedding[0]['embedding']

        #load and decrypt embedding(Hashed Key + Kyber + AES)
        data = np.load(enrolled_encrypted_path, allow_pickle=True).item()

        #DATA TO SAVE
        #========================================================================================================
        encrypted_embedding = data['encrypted'] #taken in data to save
        tag = data['tag']
        nonce = data['nonce']
        kyber_ciphertext = data['ciphertext']
        secret_key = data['kyber_secret_key']
        #========================================================================================================

        recovered_secret = Kyber512.decaps(secret_key, kyber_ciphertext) #using cipher text, for sec key
        #hash secret one more time to get the same key
        hash_obj = SHA256.new()
        hash_obj.update(recovered_secret)
        aes_key_new = hash_obj.digest()
        #decryption
        cipher = AES.new(aes_key_new, AES.MODE_GCM, nonce=nonce) #GCM
        decrypted_bytes = cipher.decrypt_and_verify(encrypted_embedding, tag) #checks for tampering with tag
        #if tag matches returns decrypted bytes
        stored_embedding = np.frombuffer(decrypted_bytes, dtype=np.float64) #embedded bytes of original face

        #Euclidean distance calculation for comparison of facial features
        #understanding of mathematics within notes, explanation of Euclidean distance
        face_feature_A = stored_embedding
        face_feature_B = np.array(current_embedding)

        distance = float(np.linalg.norm(face_feature_A - face_feature_B))
        print(f"Distance is {distance}") #might want to consider threshold here

        os.remove(temp_path)

        #================================================================================================================================
        #Threshold Comparison
        #========================================================================================================================================
        verified = 0.6 <= distance <= 0.8 #Safest distance range for threshold
        if not verified:
            print(f"This euclidian distance doesn't fit the threshold {distance}")

        return {"verified": verified, "distance": distance, "spoof_detected": False}

#figure out PostregSQL
    def pw_encryption(self):
        """
        Same process as biometric Encryption store with PostregSQL.
        """
        pass
    def pw_decryption(self):
        """
        Same process as biometirc decryption store with PostregSQL, retrive from DB
        """
        pass

#runs script
if __name__ == '__main__':
    system = BiometricSystem()
