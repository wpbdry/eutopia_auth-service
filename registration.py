import graphene
import models
import random, string
from datetime import datetime
import send_graphql

import hash
import regex
import config

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
    msg = graphene.String()

    def mutate(self, info, email):
        # Check if email is valid
        if not regex.is_valid_email(email):
            return RegisterEmail(ok=False, msg="%s is not a valid email address" % (email,))
        # Check if email is already used and check whether user has already set password
        existing_user = models.User.query.filter(models.User.email == email).first()
        if existing_user:
            existing_user_has_password = existing_user.password
            if existing_user_has_password:
                return RegisterEmail(ok=False, msg="the email address %s is already in use" % (email,))
            else:
                return RegisterEmail(ok=False, msg="you have already signed up. Please check your inbox for a code from us")
        # Create unique uid
        uid_is_unique = False
        while not uid_is_unique:
            uid = ''.join(random.choice(string.ascii_letters) for i in range(20))
            if not models.User.query.filter(models.User.uid == uid).first():
                uid_is_unique = True
        # Add user
        try:
            models.db_session.add(models.User(uid=uid, email=email))
            models.db_session.commit()
        except Exception as e:
            error = 'error adding user email: %s' % (str(e),)
            print(error)
            return RegisterEmail(ok=False, msg=error)
        # Put email in pending_signups database with unique code and send email
        code_is_unique = False
        while not code_is_unique:
            code = ''.join(random.choice(string.digits) for i in range(6))
            if not models.PendingSignup.query.filter(models.PendingSignup.code == code).first():
                code_is_unique = True
        try:
            # database
            models.db_session.add(models.PendingSignup(uid=uid, code=code, created=datetime.now()))
            models.db_session.commit()
        except Exception as e:
            error = 'error storing code in database: %s' % (str(e), )
            print(error)
            return RegisterEmail(ok=False, msg=error)
        # email
        email_body = """Hello %s! Thank you for signing up to %s. Please paste the following code to continue: %s See you soon!""" % (email, config.product_name, code)
        graphql_query = """{"query": "mutation { sendMail(recipient: \\"%s\\", subject: \\"Thanks for signing up to %s!\\", body: \\"%s\\", password: \\"%s\\") { ok, msg } }" }""" % (email, config.product_name, email_body, config.send_mail_password)
        print(graphql_query)
        try:
            # Send query to mail service
            send_graphql.send_query(
                "send_mail",
                graphql_query
            )
            return RegisterEmail(
                ok=True,
                msg='email registered correctly. Please check your inbox for a code from us'
            )
        except Exception as e:
            error = 'error sending email: %s' % (str(e), )
            print(error)
            print(e)
            return RegisterEmail(ok=False, msg=error)
