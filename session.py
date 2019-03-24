import graphene
import random, string
import datetime
import models

import hash
import config

def is_login_code_valid(email):
    pending_user = models.PendingSignup.query.filter_by(email=email).first()
    # Check time
    time_passed = datetime.datetime.now() - pending_user.created
    if time_passed > datetime.timedelta(hours=1):
        return False
    return True


def write_token(uid):
    session_token = SessionToken()
    try:
        models.db_session.add(models.Session(
            uid=uid,
            token=str(session_token),
            created=datetime.datetime.now(),
            timeout=datetime.timedelta(days=90)
        ))
        models.db_session.commit()
        return str(session_token)
    except Exception as e:
        raise Exception(str(e))


class SessionToken:
    def __init__(self):
        self.token = ''.join(random.choice(string.ascii_letters) for i in range(20))
        self.timeout = datetime.timedelta(days=90)
        self.created = datetime.datetime.now()

    def __str__(self):
        return self.token

    def is_valid(self):
        pass


class VerifyCode(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        code = graphene.String(required=True)
        password = graphene.String(required=True)

    exitcode = graphene.Int()
    token = graphene.String()
    msg = graphene.String()

    def mutate(self, info, email, code, password):
        # Check if user is already signed up
        permanent_user = models.PendingSignup.query.filter_by(email=email).first()
        if permanent_user:
            return VerifyCode(exitcode=6, msg="user has already verified code")
        # Check code
        pending_user = models.PendingSignup.query.filter_by(email=email).first()
        if not pending_user:
            return VerifyCode(exitcode=200, msg="%s is not signed up. Please sign up first." % (email, ))
        if not is_login_code_valid(email):
            return VerifyCode(exitcode=500, msg="code no longer valid")
        if pending_user.code != code:
            return VerifyCode(exitcode=3, msg="incorrect code")
        # Check that password is 8 - 32 characters
        if len(password) < config.minimum_password_length:
            return VerifyCode(exitcode=4, msg="password is too short")
        # Add user
        # Create unique uid
        uid_is_unique = False
        while not uid_is_unique:
            uid = ''.join(random.choice(string.ascii_letters) for i in range(20))
            if not models.User.query.filter_by(uid=uid).first():
                uid_is_unique = True
        # Add user
        try:
            models.db_session.add(models.User(uid=uid, email=email, password=hash.encrypt(password)))
            models.db_session.commit()
        except Exception as e:
            error = 'error adding user email: %s' % (str(e),)
            print(error)
            return VerifyCode(exitcode=5, msg=error)
        # create token
        token = write_token(uid)
        # remove code from pending signups
        models.db_session.delete(pending_user)
        return VerifyCode(exitcode=0, token=token)


class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    exitcode = graphene.Int()
    token = graphene.String()
    msg = graphene.String()

    def mutate(self, info, email, password):
        # Get user
        user = models.User.query.filter_by(email=email).first()
        if not user:
            return LoginUser(exitcode=200, msg="%s is not signed up. Please sign up first." % (email, ))
        # hash and check password
        if not hash.check(password, user.password):
            return LoginUser(exitcode=3, msg='password is incorrect')
        # Check if user is already logged in
        logged_in_user = models.Session.query.filter_by(uid=user.uid).first()
        if logged_in_user:
            # Logout
            models.db_session.delete(logged_in_user)
        # Now user has no token
        token = write_token(user.uid)
        return LoginUser(exitcode=0, token=token)


class LogoutUser(graphene.Mutation):
    class Arguments:
        token = graphene.String()

    exitcode = graphene.Int()
    msg = graphene.String()

    def mutate(self, info, token):
        logged_in_user = models.Session.query.filter_by(token=token).first()
        if not logged_in_user:
            return LoginUser(exitcode=200, msg="user was not logged in")
        try:
            models.db_session.delete(logged_in_user)
            models.db_session.commit()
            return LogoutUser(exitcode=0)
        except Exception as e:
            print('error during logout: ' + str(e))
            return LogoutUser(exitcode=3, msg='error during logout')


#TODO: Change this to a query
class IsUserLoggedIn(graphene.Mutation):
    class Arguments:
        token = graphene.String()
        password = graphene.String()

    isloggedin = graphene.Boolean()
    uid = graphene.String()
    exitcode = graphene.Int()
    msg = graphene.String()

    def mutate(self, info, token, password):
        # If password is wrong, throw error
        if password != config.my_password:
            return IsUserLoggedIn(exitcode=2, msg="authentication error")
        # Check if token is in database
        try:
            logged_in_user = models.Session.query.filter_by(token=token).first()
            if not logged_in_user:
                return IsUserLoggedIn(
                    isloggedin=False,
                    exitcode=0
                )
            # Check if token is still valid
            time_passed = datetime.datetime.now() - logged_in_user.created
            if time_passed > logged_in_user.timeout:
                return IsUserLoggedIn(
                    isloggedin=False,
                    exitcode=0
                )
            return IsUserLoggedIn(
                isloggedin=True,
                uid=logged_in_user.uid,
                exitcode=0
            )
        except Exception as e:
            error = "Error checking sessions database: %s" % (str(e), )
            return IsUserLoggedIn(
                exitcode=3,
                msg=error
            )
