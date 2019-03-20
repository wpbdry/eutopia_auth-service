import graphene
import random, string
from datetime import timedelta, datetime
from models import db_session, User as UserModel, Session as SessionModel

import hash

class SessionToken:
    def __init__(self):
        self.token = ''.join(random.choice(string.ascii_letters) for i in range(20))

    def __str__(self):
        return self.token

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
