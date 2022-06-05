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
        #print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        #print( response['Item'] if 'Item' in response else '')
        pass
    
    data = {}

    # if artist in DB 
    if 'Item' in response:
        #is_cached = False
        is_cached = redis_sto.exists(response['Item']['transaction_id']) != 0
        if cache:
           data = redis_sto.hgetall(response['Item']['transaction_id'])
           print(data)
        else:
            redis_sto.delete(response['Item']['transaction_id'])
            r=requests.get(
                f"https://api.genius.com/search?q={artist}", 
                headers={"Authorization":f"Bearer {CLIENT_ACCESS_TOKEN}"}
                )
            response = r.json()['response']['hits']

            i=1
            for song in response:
                if i>10:
                    break
                data[f'song {i}'] = song['result']['full_title']
                i+=1
                


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
        response = r.json()['response']['hits']
        i=1
        for song in response:
            if i>10:
                break
            data[f'song {i}'] = song['result']['full_title']
            i+=1

        if cache:
            redis_sto.hmset(transaction_id, data)
            redis_sto.expire(transaction_id, timedelta(days=7))
            # redis_sto.setex(
            #     transaction_id, 
            #     timedelta(days=7),
            #     value=str(data))

    return jsonify(data)


