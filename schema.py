import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import User as UserModel

import registration, session


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )


class UserConnection(relay.Connection):
    class Meta:
        node = User


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
    # register_user = RegisterUser.Field()
    register_email = registration.RegisterEmail.Field()
    verify_code = session.VerifyCode.Field()
    login_user = session.LoginUser.Field()
    logout_user = session.LogoutUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
