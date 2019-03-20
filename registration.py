import graphene
from models import db_session, User as UserModel
import re, random, string

import hash

class RegisterUser(graphene.Mutation):
    class Arguments:
        full_name = graphene.String()
        call_name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    msg = graphene.String()

    def mutate(self, info, full_name, call_name, email, password):
        # check if email is already used
        if UserModel.query.filter(UserModel.email == email).first():
            return RegisterUser(ok=False, msg='the email address \'' + email + '\' is already in use')
        # check if email is valid
        if not RegisterUser._isValidEmail(email):
            return RegisterUser(ok=False, msg=email + ' is not a valid email address')
        try:
            # TODO: check if uid is already in use. 19 octillion != infinite
            hashed_password = hash.encrypt(password)
            db_session.add(UserModel(uid=''.join(random.choice(string.ascii_letters) for i in range(20)),
                full_name=full_name, call_name=call_name, password=hashed_password, email=email))
            db_session.commit()
            return RegisterUser(ok=True, msg='user successfully created')
        except Exception as e:
            print('error creating user: ' + str(e))
            return RegisterUser(ok=False, msg='error')

    def _isValidEmail(address):
        return re.match(r"[^@]+@[^@]+\.[^@]+", address)
