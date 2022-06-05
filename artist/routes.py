import os

from flask import Blueprint, jsonify, request

import redis
from . import conect_DB
import pickle
from .models import Artist

#adding DB
client, dynamodb = conect_DB()

# conecting to local redis
redis_sto = redis.Redis()

#adding routes to app
routes = Blueprint('routes', __name__)

@routes.route("/artists/<artist>")
def artist_get(artist):

    # set artist lowercase
    artist_name = artist.lower()

    artist = Artist(name=artist_name, dynamodb=dynamodb)

    #check cache query param
    want_cache = True
    if request.args.get('cache'):
        want_cache = request.args.get('cache').lower() == "true"

    # if artist in dynamoDB 
    if artist.dynamodb_object:

        #check if we have cached info for this artist
        is_cached = redis_sto.exists(artist.transaction_id) != 0

        if want_cache and is_cached:
           data = redis_sto.get(artist.transaction_id)
           data = pickle.loads(data)
           data['used_cache'] = "true"
           artist.hits = data
           
        elif want_cache and not is_cached:
            artist.new_data_request()
            artist.cache_data(redis_sto)
            
        elif not want_cache and is_cached:
            artist.new_data_request()
            redis_sto.delete(artist.transaction_id)

    # if artist not in DynamoDB
    else:
        artist.insert_artist_dynamoDB()
        artist.new_data_request()
        
        if want_cache:
            artist.cache_data(redis_sto)


    return jsonify(artist.hits)


