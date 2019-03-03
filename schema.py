import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, User as UserModel

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

    all_users = SQLAlchemyConnectionField(UserConnection)

    # user query (test, remove when other queries are implemented)
    user = graphene.List(User, name=graphene.String())
    def resolve_user(self, info, **args):
        q = args.get('name')
        user_query = User.get_query(info)
        return user_query.filter(UserModel.name.contains(q)).all()

schema = graphene.Schema(query=Query)
