import graphene
import models
import random, string
from datetime import datetime
import gql

import hash
import regex

"""
#TODO: Remove when other registration process works
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
"""


class RegisterEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String()

    ok = graphene.Boolean()
    insession = graphene.Boolean()
    msg = graphene.String()

    def mutate(self, info, email):
        # Check if email is valid
        if not regex.is_valid_email(email):
            return RegisterEmail(ok=False, insession=False, msg="%s is not a valid email address" % email)
        # Check if email is already used
        if models.User.query.filter(models.User.email == email).first():
            return RegisterEmail(ok=False, insession=False, msg="the email address %s is already in use" % email)
        # Check if email is already pending
        if models.PendingSignup.query.filter(models.PendingSignup.email == email).first():
            return RegisterEmail(
                ok=True,
                insession=True,
                msg="%s has already signed up. Please check your email for a code from us" % email)
        # Put email in pending_signups database with unique code and send email
        code_is_unique = False
        while not code_is_unique:
            code = ''.join(random.choice(string.digits) for i in range(6))
            if not models.PendingSignup.query.filter(models.PendingSignup.code == code).first():
                code_is_unique = True
        try:
            # database
            models.db_session.add(models.PendingSignup(email=email, code=code, created=datetime.now()))
            models.db_session.commit()
            # email

            return RegisterEmail(
                ok=True, insession=False,
                msg='email registered correctly. Please check your inbox for a code from us')
        except Exception as e:
            error = 'error creating user: %s' % str(e)
            print(error)
            return RegisterEmail(ok=False, msg=error)
