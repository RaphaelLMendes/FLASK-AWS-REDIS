import os

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from botocore.exceptions import ClientError
import uuid
#import redis
from datetime import timedelta
from . import conect_DB

#adding DB
client, dynamodb = conect_DB()

#loading env variable for auth token
load_dotenv()
CLIENT_ACCESS_TOKEN = os.environ.get("CLIENT_ACCESS_TOKEN")

#redis_sto = redis.Redis()


routes = Blueprint('routes', __name__)

@routes.route("/artists/<artist>")
def artist_get(artist):

    artist = artist.lower()

    cache = True
    if request.args.get('cache'):
        cache = request.args.get('cache').lower() == "true"

    table = dynamodb.Table('flask-artists-api')

    try:
        response = table.get_item(Key={'trans_id': 1234})
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print( response['Item'])

    #check DB for artist and get transaction_id

    # if found 
    #   check datedelta to know if its still in redis or user_reset
    #   if in redis:
    #       if cache = true:
    #           return redis.info
    #       else:
    #           redis.info.delete
    #           update DB to signal user reset
    # else:
    #   add to DB (trans_ID, artist, user_reset, cached_time)
    # r = request!!!!
    # if cache = true:
    #   redis.add
    #   update DB to add current time to cached_time
    #return r



    
    #is_cached = redis_sto.exists(artist) != 0
    is_cached = False

    used_cached = False

    if cache:
        if is_cached:
            #r = redis_sto.get(artist)
            used_cached = True
        else:
            r=requests.get(
                f"https://api.genius.com/search?q={artist}", 
                headers={"Authorization":f"Bearer {CLIENT_ACCESS_TOKEN}"})
            r = r.json()['response']

            # redis_sto.setex(
            #     artist, 
            #     timedelta(days=7),
            #     value=r)

    else:
        if is_cached:
            #redis_sto.delete(artist)      
            pass

        r=requests.get(
            f"https://api.genius.com/search?q={artist}", 
            headers={"Authorization":f"Bearer {CLIENT_ACCESS_TOKEN}"})
        r = r.json()['response']


    # creating uuid to add to dynamoDB DB
    transaction_id = uuid.uuid4()

    # add to dynamoDB
    dynamoDB_obj = {
        "id": transaction_id,
        "artist": artist,
        "used_cached": used_cached,
        "user_reset_cache": not cache,
    }

    print(dynamoDB_obj)

    
    return jsonify(r)


