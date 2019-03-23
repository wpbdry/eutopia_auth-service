import graphene
import models
import random, string
from datetime import datetime
import send_graphql

import hash
import regex
import config
from session import is_login_code_valid


class RegisterEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String()

    exitcode = graphene.Int()
    msg = graphene.String()

    def mutate(self, info, email):
        # Check if email is valid
        if not regex.is_valid_email(email):
            return RegisterEmail(exitcode=2, msg="%s is not a valid email address" % (email,))
        # Check if email is already used and check whether user has already set password
        existing_user = models.User.query.filter_by(email=email).first()
        if existing_user:
            existing_user_has_password = existing_user.password
            if existing_user_has_password:
                return RegisterEmail(exitcode=3, msg="the email address %s is already in use" % (email,))
            # Check if code is still valid
            if is_login_code_valid(existing_user.uid):
                return RegisterEmail(
                    exitcode=4,
                    msg="you have already signed up. Please check your inbox for a code from us"
                )
            return RegisterEmail(
                exitcode=500,
                msg="you have already signed up. Please check your inbox for a code from us"
            )
        # Create unique uid
        uid_is_unique = False
        while not uid_is_unique:
            uid = ''.join(random.choice(string.ascii_letters) for i in range(20))
            if not models.User.query.filter_by(uid=uid).first():
                uid_is_unique = True
        # Add user
        try:
            models.db_session.add(models.User(uid=uid, email=email))
            models.db_session.commit()
        except Exception as e:
            error = 'error adding user email: %s' % (str(e),)
            print(error)
            return RegisterEmail(exitcode=6, msg=error)
        # Put email in pending_signups database with unique code and send email
        code_is_unique = False
        while not code_is_unique:
            code = ''.join(random.choice(string.digits) for i in range(6))
            if not models.PendingSignup.query.filter_by(code=code).first():
                code_is_unique = True
        try:
            # database
            models.db_session.add(models.PendingSignup(uid=uid, code=code, created=datetime.now()))
            models.db_session.commit()
        except Exception as e:
            error = 'error storing code in database: %s' % (str(e), )
            print(error)
            return RegisterEmail(exitcode=7, msg=error)
        # email
        email_body = ('Hello ' +
                      email +
                      '! Thank you for signing up to ' +
                      config.product_name +
                      '. Please paste the following code to continue: ' +
                      code +
                      ' See you soon!')
        graphql_query = '{"query": "mutation { sendMail(recipient: \\"' +\
                        email +\
                        '\\", subject: \\"Thanks for signing up to' +\
                        config.product_name +\
                        '\\", body: \\"' +\
                        email_body +\
                        '\\", password: \\"' +\
                        config.send_mail_password +\
                        '\\") { exitcode, msg } }" }'
        try:
            # Send query to mail service
            send_graphql.send_query(
                "send_mail",
                graphql_query
            )
            return RegisterEmail(
                exitcode=0,
                msg='email registered correctly. Please check your inbox for a code from us'
            )
        except Exception as e:
            error = 'error sending email: %s' % (str(e), )
            print(error)
            return RegisterEmail(exitcode=8, msg=error)
