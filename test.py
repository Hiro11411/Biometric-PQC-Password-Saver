from deepface import DeepFace
import numpy as np
from kyber_py.kyber import Kyber512
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

# # from kyber_py.kyber import Kyber512

# # pk, sk = Kyber512.keygen() #public key and secret key

# # shared_secret, ciphertext = Kyber512.encaps(pk) #encaps are returning them in the wrong order, shared_secret first cipher text next
# # recovered_secret = Kyber512.decaps(sk, ciphertext)

# # print(f"Cipher Text ${ciphertext}")
# # print(f"Recovered secret ${recovered_secret}") #seceret key
# # print(f"Match: {shared_secret == recovered_secret}")

# # #test keys

# # from kyber_py.kyber import Kyber512

# # # Generate keypair
# # pk, sk = Kyber512.keygen()
# # print(f"Public key length: {len(pk)}")
# # print(f"Secret key length: {len(sk)}")

# # # Encapsulate
# # ciphertext, shared_secret = Kyber512.encaps(pk)
# # print(f"Ciphertext length: {len(ciphertext)}")
# # print(f"Shared secret length: {len(shared_secret)}")

# # # Decapsulate
# # recovered_secret = Kyber512.decaps(sk, ciphertext)
# # print(f"Recovered secret length: {len(recovered_secret)}")

# # # Verify
# # print(f"Match: {shared_secret == recovered_secret}")
# def encryption():
#         """
#         First time capturing the your face, saving the data for future use of analysis.
#         """

#         c = int(input("Input Your Number: "))

#         if c != 512: #force testing 512
#             c = 512

#         fake_embedded = np.random.randn(c).tolist() #rand values

#         print(fake_embedded) #prints all float values

#         embedded_bytes = np.array(fake_embedded).tobytes() #encoding part, converts all into bytes

#         pk, sk = Kyber512.keygen() #public and seret key gen

#         shared_secret, ciphertext = Kyber512.encaps(pk) #encaps are returning them in the wrong order, shared_secret first cipher text next

#         #===============================================================================================================================================================================================================
#         #SHA Encryption + AES Encryption,  #sha 256 Encryption -> converts to AES key format, end goal Shared_secret == secret
#         #===============================================================================================================================================================================================================

#         new_SHA = SHA256.new()

#         new_SHA.update(shared_secret) #add shared secret to the SHA key

#         aes_key_raw = new_SHA.digest() #convert into bytes

#         #encrypt with AES, nonce number so that each combination is different

#         nonce = get_random_bytes(12)  #completely different thing from SHA

#         cipher = AES.new(aes_key_raw, AES.MODE_GCM, nonce=nonce) #combination of all 3

#         encrypted_embedding, tag = cipher.encrypt_and_digest(embedded_bytes) #tamper detector using tag, so attackers can't change your data

#         #save encrypted version and set it into a path
       
#         data_to_save = {
#             'encrypted': encrypted_embedding,
#             'tag': tag,
#             'nonce': nonce,
#             'ciphertext': ciphertext,
#             'kyber_secret_key': sk
#         }

#         print(data_to_save) #test print data

# encryption() #works for now, now just need to figure out how to save data and debug, focus on decryption first

# def decryption(self, face_roi, user_id):
#         """
#         Compares your first and tries to verify your face.
#         """

#         #path finding

#         enrolled_encrypted_path = f"{self.enrolled_dir}_{user_id}_encrypted.npy"

#         if not os.path.exists(enrolled_path):
#             print("No enrolled data for this user") #link this back to your front end
#             return False

#         temp_path = f"{self.temp_dir}/temp_{user_id}.png" #temp path for access
#         cv2.imwrite(temp_path, face_roi)

#         embedding = DeepFace.represent(
#             img_path=temp_path,
#             model_name="Facenet"
#         )
#         current_embedding = embedding[0]['embedding']

#         #load and decrypt embedding

#         #compare embeddings
#         print(f"Comparisson of Shared secret and Private secret ${private_secret == recovered_secret}")


#         result = DeepFace.verify(img1_path=enrolled_path, img2_path=temp_path)
        
#         # print(json.dumps(result, indent=2)) #result is a dict

#         os.remove(temp_path)
        

#         #change up here, wrong logic compare thresholds and distances
#         # if result['verified']:
#         #     print('Correct Person')
#         #     return True
#         # else:
#         #     print('Incorrect Person')
#         #     return False

#threshold testing
# Capture your face 10 times
distances = []

for i in range(10):
    face1 = capture_face()
    face2 = capture_face()  
    distance = calculate_distance(face1, face2)
    distances.append(distance)

print(f"Same person distances: {distances}")

max_same_person = max(distances)

print(f"Set threshold above: {max_same_person}")

#set range according to threshold, and keep changing until 
#finding a suitable distance
