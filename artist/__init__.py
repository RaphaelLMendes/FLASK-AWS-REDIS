from flask import Flask
from os import path
import boto3
from dotenv import load_dotenv
import os

load_dotenv()
AWS_Access_key_ID = os.environ.get("AWS_Access_key_ID")
AWS_Secret_access_key = os.environ.get("AWS_Secret_access_key")


def create_app():
    ''' Function responsible for creating the web app and define the env variables '''

    # creating flask app
    app = Flask(__name__)

    # defining environment config | Development
    app.config['SECRET_KEY'] = "hello world"



    #adding blueprint routes
    from .routes import routes
    app.register_blueprint(routes, url_prefix="/")

    return app

def conect_DB():
    client = boto3.client(
    'dynamodb',
    aws_access_key_id=AWS_Access_key_ID,
    aws_secret_access_key=AWS_Secret_access_key,
    region_name="sa-east-1"
    )
    dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_Access_key_ID,
    aws_secret_access_key=AWS_Secret_access_key,
    region_name="sa-east-1"
    )
    ddb_exceptions = client.exceptions

    create_artist_table(dynamodb, client)

    return client, dynamodb

def create_artist_table(dynamodb=None, client=None):
    if not dynamodb:
        return
    if not client:
        return

    try:
        table = client.create_table(
            TableName='Artist',
            KeySchema=[
            {
                'AttributeName': 'artist_name',
                'KeyType': 'HASH'  # Partition key
            }
                ],
            AttributeDefinitions=[
            {
                'AttributeName': 'artist_name',
                'AttributeType': 'S'
            }
 
                ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        print("Creating table")
        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName='Artist')
        print("Table created")
        
    except:
        print("Table exists")
        return

    return table


