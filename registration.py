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
        # Check if there is already an account associated with email
        existing_user = models.User.query.filter_by(email=email).first()
        if existing_user:
            return RegisterEmail(exitcode=3, msg="the email address %s is already in use" % (email,))
        # Check if email has already requested a code
        pending_user = models.PendingSignup.query.filter_by(email=email).first()
        if pending_user:
            if is_login_code_valid(pending_user.email):
                return RegisterEmail(
                    exitcode=4,
                    msg="you have already signed up. Please check your inbox for a code from us"
                )
            return RegisterEmail(
                exitcode=500,
                msg="you have already signed up. Please check your inbox for a code from us"
        )
        # Put email in pending_signups database with unique code and send email
        code_is_unique = False
        while not code_is_unique:
            code = ''.join(random.choice(string.digits) for i in range(6))
            if not models.PendingSignup.query.filter_by(code=code).first():
                code_is_unique = True
        try:
            # database
            models.db_session.add(models.PendingSignup(email=email, code=code, created=datetime.now()))
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
