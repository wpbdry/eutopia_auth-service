from passlib.hash import sha256_crypt

"""
password = sha256_crypt.encrypt("password")
password2 = sha256_crypt.encrypt("password")

print(password)
print(password2)

print(sha256_crypt.verify("password", password))
"""

def encrypt(password):
    return sha256_crypt.encrypt(password)

def check(password, hash):
    return sha256_crypt.verify(password, hash)