import cv2
from deepface import DeepFace
import numpy as np
from kyber_py.kyber import Kyber512
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
import pickle
import os

#cascade is used for speed, recognition of the different prompts
#haar features used, check notes
class BiometricSystem: 
    def __init__(self):
        #video section
        video=self.cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') #calling self, to later access it in the future

        #file directory section
        self.enrolled_dir = "data/enrolled_faces"
        self.temp_dir = "data/temp_faces"
        os.makedirs(self.enrolled_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)


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
        #write the function here tomorrow
        #analyzation of emotion
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
        emotion_dominant = result[0]['dominant_emotion'] #returns the dominant emotion, retrived FROM THE DICT of emotions, always first column
        emotion = result[0]['emotion'] #returns the emotions, and all the values of emotions
        confidence = emotion[emotion_dominant] / 100.0 #emotional confidence indicator as a percentage
        print(confidence, emotion, emotion_dominant)
        return emotion_dominant, confidence #parameter passing here 
    
    def biometirc_encryption(self, face_roi, user_id):
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
        embedding = DeepFace.represent(
                img_path = temp_path,
                model_name="Facenet"
            )

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
        
        print(f"Face Enrolled for ${user_id}!") #enrolled msg
        
        os.remove(temp_path) #remove path so cant trace

        return temp_path #for future use and calling

    def biometric_decryption(self, face_roi, user_id):
        """
        Compares your first and tries to verify your face.
        """

        #Comparison of Originally Encrypted Path
        enrolled_encrypted_path = f"{self.enrolled_dir}_{user_id}_encrypted.npy"

        if not os.path.exists(enrolled_path):
            print("No enrolled data for this user") #link this back to your front end
            return False

        temp_path = f"{self.temp_dir}/temp_{user_id}.png" #temp path for access
        cv2.imwrite(temp_path, face_roi)

        embedding = DeepFace.represent(
            img_path=temp_path,
            model_name="Facenet"
        )

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
        aes_key_new = has_obj.digest()
        #decryption
        cipher = AES.new(aes_key_new, AES.MODE_GCM, nonce=nonce) #GCM
        decrypted_bytes = cipher.decrypt_and_verify(encrypted_embedding, tag) #checks for tampering with tag
        #if tag matches returns decrypted bytes
        stored_embedding = np.frombuffer(decrypted_bytes, dtype=np.float64).tolist() #embedded bytes of original face

        #Euclidean distance calculation for comparison of facial features
        #understanding of mathematics within notes, explanation of Euclidean distance

        value1 = [] #empty list add the difference in values for euc calc
        face_feature_A = stored_embedding
        face_feature_B = current_embedding

        #threshold calculation
        for i in range(len(face_feature_A)):
            difference = face_feature_A[i] - face_feature_B[i]
            squared = difference ** 2
            value1.append[squared]
            sum_of_squares = sum(value1)
            distance  = sqrt(sum_of_squares)
            print(f"Distance is ${distance}") #might want to consider threshold here
            max_same_person = max(distances)
            print(f"Set threshold above: {max_same_person}") #for debugging and setting purposes right now
        
        #================================================================================================================================
        #Threshold Comparison
        #========================================================================================================================================

            if 0.6 <= distance <= 0.8: #Safest distance range for threshold
                return distance
            else:
                print(f"This euclidian distance doesn't fit the threshold ${distance}")
                return 0

        os.remove(temp_path)

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
# #Only used for testing within local
#     def main(self):
#         #call both functions in main

#         id = self.id_input() #gets the original ID, and inputs here
#         count = 0 #counter
#         while True: #Main Loop
#             try:     
#                 ret, frame = self.video.read() #when camera empty, _src.empty() in func

#                 if not ret: #meaning that if Camera doesn't work continues running 
#                     video.read() #fix here later main problem
#                     continue

#                 gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #START IN GRAY COLOR, using BGR FORMAT NOT RGB

#                 faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
#                 for (x, y, w, h) in faces: #tuple, takes tuple data and uses it within rectangle
#                     count=count+1 #counter to count the amount of photos taken, then translate
                        
#                     face_roi = frame[y:y+h, x:x+w]#reigon of interest, face

#                     emotion_dominant, confidence = self.emotional_analyzer(face_roi) #takes in ONLY face_roi, returns variables and determines theresholds
#                     #passing parameter succesfully here.

#                     cv2.imwrite('datasets/User.'+str(id)+"."+str(count)+".jpg", gray[y:y+h, x:x+w])
#                     cv2.rectangle(frame, (x,y), (x+w, y+h), (50, 50, 225), 1) #tuple data used within here
#                     cv2.putText(frame, emotion_dominant, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2) #emotion shown

#                     #constructs rectange

#                     cv2.imshow("Frame", frame)
                    
#                     key = cv2.waitKey(1) #waiting for key press in 1 ms, if key press then ..
                    
#                     if key==ord('q'):
#                         break
#                     # if count > 500: #deletes program, when q key is pressed
#                     #     break #break program

#                     #remember to handle errors !!!!!!!! Important asf

#                     encryption() #mainly work on functions here tmr!!
#                     decryption()
#             except cv2.error as e:
#                 print(f"CV2 ERR {e}")
#                 continue

# video.release() #after done closes the webcam connectio

# cv2.destroyAllWindows() #Closes all OpenCV windows
# print("Closed File, Frame")
#should implement this here with main function, better for script, and safer/more efficient

#encoding for first time vs encoding for second time

#runs script
if __name__ == '__main__':
    system = BiometricSystem()
    # system.main()
