import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import random
import string
from models import db_session, User as UserModel

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
        try:
            # TODO: check if uid is already in use. 19 octillion != infinite
            db_session.add(UserModel(uid=''.join(random.choice(string.ascii_lowercase) for i in range(20)),
                full_name=full_name, call_name=call_name, password=password, email=email))
            db_session.commit()
            return RegisterUser(ok=True, msg='user successfully created')
        except Exception as e:
            print('error creating user: ' + str(e))
            return RegisterUser(ok=False, msg='error')

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

schema = graphene.Schema(query=Query, mutation=Mutation)
