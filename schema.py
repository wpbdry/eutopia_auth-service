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

schema = graphene.Schema(query=Query)
