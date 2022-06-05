# Artist API REST

The current project was developed to follow a simple real world python flask test case.

1. Create a REST API in Python (FLASK) that consumes the Genius API ([Documentation](https://docs.genius.com/#/getting-started-h1)) that, given an artist, lists the 10 most popular songs of the searched artist, saving a transaction id in the format uuid version 4, name of the artist searched, in a collection in DynamoDB, the data with the return of the API query must be saved in Redis for 7 days. 
2. When searching for an artist through the API, check if there is a saved transaction and if it is available in cache (Redis), if it exists, send the Redis data, otherwise, follow those informed in step 1. 
3. The query must allow passing via query string the option to keep the data in cache, if sent the parameter cache=False clear the Redis transaction and update DynamoDB with the option chosen by the user, not sending the parameter indicates that cached data must be used.

## Installation

Clone this repo to install. Then run the following commands

```bash
cd FLASK-AWS-REDIS/
```
you can use whatever env you want, in this case I will make my own virtualenv
```bash
virtualenv venv
```
```bash
source venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
Now you need to fill out the .env.sample file with the api authorization keys. Then rename that file to .env

Now finaly run:

```bash
python app.py
```

Acess the application on http://127.0.0.1:5000/artists/(put name of artist here)

Also, for this to work you will need to instal redis localy on your machine, please follow [this](https://redis.io/docs/getting-started/installation/install-redis-on-windows/) tutorial.