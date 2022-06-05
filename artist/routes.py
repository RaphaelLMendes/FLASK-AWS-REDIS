import os

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from botocore.exceptions import ClientError
import uuid
import redis
from datetime import timedelta
from . import conect_DB
import json
import pickle

#adding DB
client, dynamodb = conect_DB()

#loading env variable for auth token
load_dotenv()
CLIENT_ACCESS_TOKEN = os.environ.get("CLIENT_ACCESS_TOKEN")

redis_sto = redis.Redis()


routes = Blueprint('routes', __name__)

@routes.route("/artists/<artist>")
def artist_get(artist):

    # set artist lowercase
    artist = artist.lower()

    #check cache query param
    cache = True
    if request.args.get('cache'):
        cache = request.args.get('cache').lower() == "true"

    # conecting to dynamoDB table
    table = dynamodb.Table('Artist')

    #check DB for artist and get doc
    try:
        response = table.get_item(Key={'artist_name': artist})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        #print( response['Item'] if 'Item' in response else '')
        pass
    
    data = {}

    # if artist in dynamoDB 
    if 'Item' in response:
        
        #check if we have cached info for this artist
        is_cached = redis_sto.exists(response['Item']['transaction_id']) != 0

        if cache and is_cached:
           data = redis_sto.get(response['Item']['transaction_id'])
           data = pickle.loads(data)
           data['used_cache'] = "true"
           print(data)
        else:
            if is_cached:
                redis_sto.delete(response['Item']['transaction_id'])
            r=requests.get(
                f"https://api.genius.com/search?q={artist}", 
                headers={"Authorization":f"Bearer {CLIENT_ACCESS_TOKEN}"}
                )
            data = r.json()['response']
            if cache:
                p_mydict = pickle.dumps(data)
                redis_sto.setex(
                    response['Item']['transaction_id'], 
                    timedelta(days=7),
                    value=p_mydict)

    else:
        # creating uuid to add to dynamoDB DB
        transaction_id = str(uuid.uuid4())
        response = table.put_item(
            Item={
                'artist_name': artist,
                'transaction_id': transaction_id
            }
        )

        r=requests.get(
            f"https://api.genius.com/search?q={artist}", 
            headers={"Authorization":f"Bearer {CLIENT_ACCESS_TOKEN}"}
            )
        data = r.json()['response']


        if cache:
            p_mydict = pickle.dumps(data)
            redis_sto.setex(
                transaction_id, 
                timedelta(days=7),
                value=p_mydict)

    return jsonify(data)


