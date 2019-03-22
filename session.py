import graphene
import random, string
import datetime
import models

import hash


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

    ok = graphene.Boolean()
    token = graphene.String()
    msg = graphene.String()
    codeexpired = graphene.Boolean()

    def mutate(self, info, email, code, password):
        # Get user
        #user = models.User.query.filter(models.User.email == email).first()
        print(email)
        user = models.User.query.filter_by(email=email).first()
        print(user)
        if not user:
            return LoginUser(ok=False, msg="%s is not signed up. Please sign up first." % (email, ))
        if code and password:
            return LoginUser(ok=False, msg="Please provide either login code OR password")
        elif code:
            # If user has set password, disallow login by code
            if user.password:
                return LoginUser(ok=False, msg="You have already set a password. Please use your password to log in")
            pending_user = models.PendingSignup.query.filter_by(uid=user.uid).first()
            # Check time
            time_passed = datetime.datetime.now() - pending_user.created
            if time_passed > datetime.timedelta(hours=1):
                return LoginUser(ok=False, codeexpired=True, msg="Your code has expired. Please request a new code")
            # Check code
            if pending_user.code != code:
                return LoginUser(ok=False, msg="Incorrect code. Please try again")
            # Else continue to token
        elif password:
            # If user has not set password, tell her
            if not user.password:
                return LoginUser(ok=False, msg="You have not yet set a password. Please visit our landing page to log in")
            # hash and check password
            if not hash.check(password, user.password):
                return LoginUser(ok=False, msg='password is incorrect')
            # Else continue to token
        else:
            return LoginUser(ok=False, msg="Please provide either login code or password")
        # Continue with token
        logged_in_user = models.Session.query.filter_by(uid=user.uid).first()
        if logged_in_user:
            # if user has valid token
            if (logged_in_user.created + logged_in_user.timeout) > datetime.datetime.now():
                return LoginUser(ok=True, msg='user already logged in', token=logged_in_user.token)
            # if user has invalid token
            else:
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
            return LoginUser(ok=True, token=session_token, msg="successfully logged in")
        except Exception as e:
            error = 'error during login: ' + str(e)
            print(error)
            return LoginUser(ok=False, msg=error)



"""
class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    msg = graphene.String()
    token = graphene.String()

    def mutate(self, info, email, password):
        # user = User.get_query(info).filter(UserModel.email == email).first()
        user = UserModel.query.filter(UserModel.email == email).first()
        # check if user exists
        if not user:
            return LoginUser(ok=False, msg=email + ' doesn\'t exist')
        # check if password is incorrect
        if not hash.check(password, user.password):
            return LoginUser(ok=False, msg='password is incorrect')
        # check if already logged in
        if db_session.query(SessionModel).filter(SessionModel.uid == user.uid).first():
            return LoginUser(ok=False, msg='user already logged in')
        # login successful
        session_token = SessionToken()
        try:
            db_session.add(SessionModel(uid=user.uid, token=str(session_token),
                created=datetime.now(), timeout=timedelta(hours=1)))
            db_session.commit()
            return LoginUser(ok=True, msg='login successful', token=session_token)
        except Exception as e:
            print('error during login: ' + str(e))
            return LoginUser(ok=False, msg='error during login')
"""

class LogoutUser(graphene.Mutation):
    class Arguments:
        token = graphene.String()

    ok = graphene.Boolean()
    msg = graphene.String()

    def mutate(self, info, token):
        try:
            SessionModel.query.filter(SessionModel.token == token).delete()
            db_session.commit()
            return LogoutUser(ok=True, msg='successfully logged out')
        except Exception as e:
            print('error during logout: ' + str(e))
            return LogoutUser(ok=False, msg='error during logout')
