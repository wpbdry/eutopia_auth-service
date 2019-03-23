import graphene
import random, string
import datetime
import models

import hash


def is_login_code_valid(uid):
    pending_user = models.PendingSignup.query.filter_by(uid=uid).first()
    # Check time
    time_passed = datetime.datetime.now() - pending_user.created
    if time_passed > datetime.timedelta(hours=1):
        return False
    return True


class SessionToken:
    def __init__(self):
        self.token = ''.join(random.choice(string.ascii_letters) for i in range(20))
        self.timeout = datetime.timedelta(days=90)
        self.created = datetime.datetime.now()

    def __str__(self):
        return self.token

    def is_valid(self):
        pass


class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        code = graphene.String(required=False, default_value=False)
        password = graphene.String(required=False, default_value=False)

    exitcode = graphene.Int()
    token = graphene.String()
    msg = graphene.String()

    def mutate(self, info, email, code, password):
        # Get user
        user = models.User.query.filter_by(email=email).first()
        if not user:
            return LoginUser(exitcode=2, msg="%s is not signed up. Please sign up first." % (email, ))
        if code and password:
            return LoginUser(exitcode=3, msg="Please provide either login code OR password")
        elif code:
            # If user has set password, disallow login by code
            if user.password:
                return LoginUser(exitcode=4, msg="You have already set a password. Please use your password to log in")
            pending_user = models.PendingSignup.query.filter_by(uid=user.uid).first()
            # Check time
            if not is_login_code_valid(pending_user.uid):
                return LoginUser(exitcode=500, msg="Your code has expired. Please request a new code")
            # Check code
            if pending_user.code != code:
                return LoginUser(exitcode=6, msg="Incorrect code. Please try again")
            # Else continue to token
        elif password:
            # If user has not set password, tell her
            if not user.password:
                return LoginUser(
                    exitcode=7,
                    msg="You have not yet set a password. Please visit our landing page to log in"
                )
            # hash and check password
            if not hash.check(password, user.password):
                return LoginUser(exitcode=8, msg='password is incorrect')
            # Else continue to token
        else:
            return LoginUser(exitcode=3, msg="Please provide either login code or password")
        # Continue with token
        logged_in_user = models.Session.query.filter_by(uid=user.uid).first()
        if logged_in_user:
            # Logout
            models.db_session.delete(logged_in_user)
        # Now user has no token
        session_token = SessionToken()
        try:
            models.db_session.add(models.Session(
                uid=user.uid,
                token=str(session_token),
                created=datetime.datetime.now(),
                timeout=datetime.timedelta(days=90)
            ))
            models.db_session.commit()
            return LoginUser(exitcode=0, token=session_token)
        except Exception as e:
            error = 'error during login: ' + str(e)
            print(error)
            return LoginUser(exitcode=9, msg=error)


class LogoutUser(graphene.Mutation):
    class Arguments:
        token = graphene.String()

    exitcode = graphene.Int()
    msg = graphene.String()

    def mutate(self, info, token):
        logged_in_user = models.Session.query.filter_by(token=token).first()
        if not logged_in_user:
            return LoginUser(exitcode=2, msg="user was not logged in")
        try:
            models.db_session.delete(logged_in_user)
            models.db_session.commit()
            return LogoutUser(exitcode=0)
        except Exception as e:
            print('error during logout: ' + str(e))
            return LogoutUser(exitcode=3, msg='error during logout')
