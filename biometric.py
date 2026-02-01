import cv2
from deepface import DeepFace

#cascade is used for speed, recognition of the different prompts
#haar features used, check notes
class BiometricSystem: 
    def __init__(self):
        """
        
        """
        video=self.cv2.VideoCapture(0)

        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') #calling self, to later access it in the future

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
        emotion_dominant = result[0]['dominant_emotion'] #returns the dominant emotion, retrived FROM THE DICT of emotions
        emotion = result[0]['emotion'] #returns the emotions, and all the values of emotions
        confidence = emotion[emotion_dominant] / 100.0 #emotional confidence indicator as a percentage
        print(confidence, emotion, emotion_dominant)
        return emotion_dominant, confidence #parameter passing here 

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

video.release() #after done closes the webcam connection
cv2.destroyAllWindows() #Closes all OpenCV windows
print("Closed File, Frame")
#should implement this here with main function, better for script, and safer/more efficient

#runs script
if __name__ == '__main__':
    system = BiometricSystem()
    system.main()
    