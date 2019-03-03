import graphene
from graphene import relay
from models import db_session

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    query_test = graphene.String(argument=graphene.String(default_value="it's working"))
    def resolve_query_test(self, info, argument):
        return argument

schema = graphene.Schema(query=Query)
