import azure.functions as func
from azure.keyvault.secrets import SecretClient
from config import config
import pymongo
import json

key_client = SecretClient(vault_url=config.KVUri, credential=config.credential)

CONN_STRING_KEY = config.conn_secret_key
DB_NAME = config.db_name
CONTAINER_NAME = config.container_name
CONN_STRING = key_client.get_secret(CONN_STRING_KEY)

def get_story(req, coll):

    req_body = req.get_json()

    try:
        story = coll.find_one({
        "story_id": req_body.get('story_id'),
        })

        return func.HttpResponse( json.dumps({
            'message': "story successfully found",
            'data': story
            }),status_code=201)
    except:
        return func.HttpResponse("unable to create new story, please try again.", status_code=400) 


def main(req: func.HttpRequest) -> func.HttpResponse:
    

    try:

        client = pymongo.MongoClient(CONN_STRING.value)

        collection = client[DB_NAME].get_collection(CONTAINER_NAME)

        return get_story(req, collection)

    except pymongo.errors.ServerSelectionTimeoutError:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
        
    
