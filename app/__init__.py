import os
from flask import Flask
from app.models import db
from flask_migrate import Migrate
from graphql_server.flask import GraphQLView
from app.schema import schema


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)


app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))

@app.route('/')
def index():
    return 'Hello this is the GraphQL API!'


