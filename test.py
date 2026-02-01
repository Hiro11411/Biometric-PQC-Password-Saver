from kyber_py.kyber import Kyber512

pk, sk = Kyber512.keygen()

shared_secret = Kyber512.decaps(pk, sk)
print(pk)
print(sk)