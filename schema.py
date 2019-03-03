import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy import *
import random
import string
import re
from datetime import timedelta, datetime
from models import db_session, User as UserModel, Session as SessionModel

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )

class UserConnection(relay.Connection):
    class Meta:
        node = User

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
        if len(User.get_query(info).filter(UserModel.email.contains(email)).all()) > 0:
            return RegisterUser(ok=False, msg='the email address \'' + email + '\' is already in use')
        # check if email is valid
        if not RegisterUser._isValidEmail(email):
            return RegisterUser(ok=False, msg=email + ' is not a valid email address')
        try:
            # TODO: check if uid is already in use. 19 octillion != infinite
            db_session.add(UserModel(uid=''.join(random.choice(string.ascii_letters) for i in range(20)),
                full_name=full_name, call_name=call_name, password=password, email=email))
            db_session.commit()
            return RegisterUser(ok=True, msg='user successfully created')
        except Exception as e:
            print('error creating user: ' + str(e))
            return RegisterUser(ok=False, msg='error')

    def _isValidEmail(address):
        return re.match(r"[^@]+@[^@]+\.[^@]+", address)

class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    msg = graphene.String()
    token = graphene.String()

    def mutate(self, info, email, password):
        user = User.get_query(info).filter(UserModel.email == email).first()
        # check if user exists
        if not user:
            return LoginUser(ok=False, msg=email + ' doesn\'t exist')
        # check if password is correct
        if user.password != password:
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

class SessionToken:
    def __init__(self):
        self.token = ''.join(random.choice(string.ascii_letters) for i in range(20))

    def __str__(self):
        return self.token

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    query_test = graphene.String(argument=graphene.String(default_value="it's working"))
    def resolve_query_test(self, info, argument):
        return argument

    # list of all users (TODO: remove)
    all_users = SQLAlchemyConnectionField(UserConnection)

    # query user by name (TODO: remove when other queries are implemented)
    user = graphene.List(User, name=graphene.String())
    def resolve_user(self, info, **args):
        return User.get_query(info).filter(UserModel.name.contains(args.get('name'))).all()

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
