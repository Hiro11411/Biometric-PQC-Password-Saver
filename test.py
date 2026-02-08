from kyber_py.kyber import Kyber512

pk, sk = Kyber512.keygen() #public key and secret key

shared_secret, ciphertext = Kyber512.encaps(pk) #encaps are returning them in the wrong order, shared_secret first cipher text next
recovered_secret = Kyber512.decaps(sk, ciphertext)

print(f"Cipher Text ${ciphertext}")
print(f"Recovered secret ${recovered_secret}") #seceret key
print(f"Match: {shared_secret == recovered_secret}")

# #test keys

# from kyber_py.kyber import Kyber512

# # Generate keypair
# pk, sk = Kyber512.keygen()
# print(f"Public key length: {len(pk)}")
# print(f"Secret key length: {len(sk)}")

# # Encapsulate
# ciphertext, shared_secret = Kyber512.encaps(pk)
# print(f"Ciphertext length: {len(ciphertext)}")
# print(f"Shared secret length: {len(shared_secret)}")

# # Decapsulate
# recovered_secret = Kyber512.decaps(sk, ciphertext)
# print(f"Recovered secret length: {len(recovered_secret)}")

# # Verify
# print(f"Match: {shared_secret == recovered_secret}")
