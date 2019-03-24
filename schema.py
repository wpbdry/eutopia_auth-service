import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import models

import registration, session, config


class Session(SQLAlchemyObjectType):
    class Meta:
        model = models.Session
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    query_test = graphene.String(argument=graphene.String(default_value="it's working"))

    def resolve_query_test(self, info, argument):
        return argument

    # check if someone is logged in with token
    session = graphene.List(Session, token=graphene.String())

    def resolve_session(self, info, token):
        return Session.get_query(info).filter_by(token=token).all()

    # DOESN'T CHECK IF TOKEN IS VALID


class Mutation(graphene.ObjectType):
    # register_user = RegisterUser.Field()
    register_email = registration.RegisterEmail.Field()
    request_new_code = registration.RequestNewCode.Field()
    is_code_valid = registration.IsCodeValid.Field()
    verify_code = session.VerifyCode.Field()
    login_user = session.LoginUser.Field()
    logout_user = session.LogoutUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
