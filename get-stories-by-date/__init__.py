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

def get_stories_by_date(coll):

    try:
        stories_by_user = coll.find().sort({"created_at": 1})


        return func.HttpResponse( json.dumps({
            'message': "stories successfully found",
            'data': stories_by_user
            }),status_code=201)
    except:
        return func.HttpResponse("unable to create new story, please try again.", status_code=400) 


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    client = pymongo.MongoClient(CONN_STRING.value)

    try:
        client.server_info() # validate connection string
        collection = client[DB_NAME].get_collection(CONTAINER_NAME)

        return get_stories_by_date(collection)

    except pymongo.errors.ServerSelectionTimeoutError:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
