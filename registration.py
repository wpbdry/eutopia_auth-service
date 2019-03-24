import graphene
import models
import random, string
from datetime import datetime
import send_graphql

import regex
import config
from session import is_login_code_valid


def send_signup_email(email, code):
    email_body = ('Hello ' +
                  email +
                  '! Thank you for signing up to ' +
                  config.product_name +
                  '. Please paste the following code to continue: ' +
                  code +
                  ' See you soon!')
    graphql_query = '{"query": "mutation { sendMail(recipient: \\"' + \
                    email + \
                    '\\", subject: \\"Thanks for signing up to' + \
                    config.product_name + \
                    '\\", body: \\"' + \
                    email_body + \
                    '\\", password: \\"' + \
                    config.send_mail_password + \
                    '\\") { exitcode, msg } }" }'
    try:
        # Send query to mail service
        send_graphql.send_query(
            "send_mail",
            graphql_query
        )
        return {
            "exitcode": 0,
            "msg": 'email registered correctly. Please check your inbox for a code from us'
        }
    except Exception as e:
        error = 'error sending email: %s' % (str(e),)
        print(error)
        return {
            "exitcode": 8,
            "msg": error
        }


def generate_unique_code():
    code_is_unique = False
    while not code_is_unique:
        code = ''.join(random.choice(string.digits) for i in range(6))
        if not models.PendingSignup.query.filter_by(code=code).first():
            code_is_unique = True
    return code


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
        code = generate_unique_code()
        try:
            # database
            models.db_session.add(models.PendingSignup(email=email, code=code, created=datetime.now()))
            models.db_session.commit()
        except Exception as e:
            error = 'error storing code in database: %s' % (str(e), )
            print(error)
            return RegisterEmail(exitcode=700, msg=error)
        # email
        result = send_signup_email(email, code)
        if result["exitcode"] == 0:
            return RegisterEmail(exitcode=0)
        return RegisterEmail(exitcode=8, msg=result["msg"])


class RequestNewCode(graphene.Mutation):
    class Arguments:
        email = graphene.String()

    exitcode = graphene.String()
    msg = graphene.String()

    def mutate(self, info, email):
        # Check that email is already in pending signups
        pending_user = models.PendingSignup.query.filter_by().first()
        if not pending_user:
            return RequestNewCode(exitcode=2, msg="user has never requested a code")
        # Create code and write to database
        code = generate_unique_code()
        try:
            pending_user.code = code
            models.db_session.commit()
            return RequestNewCode(exitcode=0)
        except Exception as e:
            error = "error writing new code to database: %s" % (str(e), )
            return RequestNewCode(exitcode=700, msg=error)


class IsCodeValid(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        code = graphene.String(required=True)

    exitcode = graphene.Int()
    isvalid = graphene.Boolean()
    msg = graphene.String()

    def mutate(self, info, code, email):
        pending_user = models.PendingSignup.query.filter_by(email=email)
        if not pending_user:
            return IsCodeValid(exitcode=2, msg="user never requested a code")
        is_valid = is_login_code_valid(pending_user.email)
        if not is_valid:
            return IsCodeValid(exitcode=0, isvalid=False, msg="code has expired")
        if pending_user.code != code:
            return IsCodeValid(exitcode=0, isvalid=False, msg="incorrect code")
        return IsCodeValid(exitcode=0, isvalid=True)
