from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS

from models import db_session
from schema import schema
import config

app = Flask(__name__)
CORS(app)
app.debug = True

app.add_url_rule(
    '/auth',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True, # GraphiQL interface
        context={'session': db_session}
    )
)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(
        host=config.flask_host,
        port=config.flask_port
    )
