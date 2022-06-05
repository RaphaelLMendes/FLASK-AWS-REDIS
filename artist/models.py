from botocore.exceptions import ClientError
import uuid
import requests
import os
import pickle
from datetime import timedelta

from dotenv import load_dotenv

#loading env variable for auth token
load_dotenv()

CLIENT_ACCESS_TOKEN = os.environ.get("GENIUS_CLIENT_ACCESS_TOKEN")

class Artist():

    def __init__(self, name, dynamodb):
        self.artist_name = name
        self.transaction_id = ""
        self.hits = {}
        self.dynamodb = dynamodb
        self.dynamodb_object = self._get_artist_dynamoDB()

    def _get_artist_dynamoDB(self):
    
        table = self.dynamodb.Table('Artist')
    
        try:
            response = table.get_item(Key={'artist_name': self.artist_name})
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                self.transaction_id = response['Item']['transaction_id']
            return response['Item'] if 'Item' in response else None
    
    def insert_artist_dynamoDB(self):
    
        table = self.dynamodb.Table('Artist')

        self.transaction_id = str(uuid.uuid4())
        self.dynamodb_object = table.put_item(
            Item={
                'artist_name': self.artist_name,
                'transaction_id': self.transaction_id
            }
        )

    def new_data_request(self):
        r=requests.get(
            f"https://api.genius.com/search?q={self.artist_name}", 
            headers={"Authorization":f"Bearer {CLIENT_ACCESS_TOKEN}"}
            )
        self.hits = r.json()['response']
    
    def cache_data(self, redis_sto):
        p_mydict = pickle.dumps(self.hits)
        redis_sto.setex(
            self.transaction_id, 
            timedelta(days=7),
            value=p_mydict)