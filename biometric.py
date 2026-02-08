import cv2
from deepface import DeepFace
from numpy import np
from kyber_py.kyber import Kyber512
from Crypto.random import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
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
    
    def first_encode(self, face_roi, user_id):
        """
        First time capturing the your face, saving the data for future use of analysis.
        """

        #===============================================================================================================================================================================================================
        #facial recognition part
        #===============================================================================================================================================================================================================
        temp_path = f"{self.temp_dir}/user_{user_id}.jpg"

        cv2.imwrite(temp_path, face_roi)


        #extract embedding
        embedding = DeepFace.represent(
                img_path = temp_path,
                model_name="Facenet"
            )

        embedded = embedding[0]['embedding'] #list of embedded values, convert in bytes

        embedded_bytes = np.array(embedded).tobytes() #encoding part

        #===============================================================================================================================================================================================================
        #Kyber Encryption
        #===============================================================================================================================================================================================================

        pk, sk = Kyber512.keygen() #public and seret key gen

        shared_secret, ciphertext = Kyber512.encaps(pk) #encaps are returning them in the wrong order, shared_secret first cipher text next

        #===============================================================================================================================================================================================================
        #SHA Encryption + AES Encryption,  #sha 256 Encryption -> converts to AES key format 
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
        np.save(encrypted_path, data_to_save)
        
        print(f"Face Enrolled for ${user_id}!")
        
        return temp_path #for future use and calling
        
        os.remove(temp_path)

    def second_encode(self, face_roi, user_id):
        """
        Compares your first and tries to verify your face.
        """
        #comparisson part
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

        #load and decrypt embedding

        #compare embeddings
        print(f"Comparisson of Shared secret and Private secret ${private_secret == recovered_secret}")


        result = DeepFace.verify(img1_path=enrolled_path, img2_path=temp_path)
        
        # print(json.dumps(result, indent=2)) #result is a dict

        os.remove(temp_path)
        

        #change up here, wrong logic compare thresholds and distances
        # if result['verified']:
        #     print('Correct Person')
        #     return True
        # else:
        #     print('Incorrect Person')
        #     return False
        

    def main(self):
        id = self.id_input() #gets the original ID, and inputs here
        count = 0 #counter
        while True: #Main Loop
            try:     
                ret, frame = self.video.read() #when camera empty, _src.empty() in func

                if not ret: #meaning that if Camera doesn't work continues running 
                    video.read() #fix here later main problem
                    continue

                gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #START IN GRAY COLOR, using BGR FORMAT NOT RGB

                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces: #tuple, takes tuple data and uses it within rectangle
                    count=count+1 #counter to count the amount of photos taken, then translate
                        
                    face_roi = frame[y:y+h, x:x+w]#reigon of interest, face

                    emotion_dominant, confidence = self.emotional_analyzer(face_roi) #takes in ONLY face_roi, returns variables and determines theresholds
                    #passing parameter succesfully here.

                    cv2.imwrite('datasets/User.'+str(id)+"."+str(count)+".jpg", gray[y:y+h, x:x+w])
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (50, 50, 225), 1) #tuple data used within here
                    cv2.putText(frame, emotion_dominant, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2) #emotion shown

                    #constructs rectange

                    cv2.imshow("Frame", frame)
                    
                    key = cv2.waitKey(1) #waiting for key press in 1 ms, if key press then ..
                    
                    if key==ord('q'):
                        break
                    # if count > 500: #deletes program, when q key is pressed
                    #     break #break program

                    #remember to handle errors !!!!!!!! Important asf
            except cv2.error as e:
                print(f"CV2 ERR {e}")
                continue

video.release() #after done closes the webcam connectio

cv2.destroyAllWindows() #Closes all OpenCV windows
print("Closed File, Frame")
#should implement this here with main function, better for script, and safer/more efficient

#encoding for first time vs encoding for second time

#runs script
if __name__ == '__main__':
    system = BiometricSystem()
    system.main()
    