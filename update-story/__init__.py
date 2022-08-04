import azure.functions as func
from azure.keyvault.secrets import SecretClient
from config import config
import pymongo

key_client = SecretClient(vault_url=config.KVUri, credential=config.credential)

CONN_STRING_KEY = config.conn_secret_key
DB_NAME = config.db_name
CONTAINER_NAME = config.container_name
CONN_STRING = key_client.get_secret(CONN_STRING_KEY)

def update_story(req, collection):
    
    req_body = req.get_json()
    try:
        collection.update_one({
        "story_id": req_body.get('story_id'),
        "author_id": req.params.get('user_id')
        }, {"$set": req_body.get()})

        return func.HttpResponse(f"Story successfully deleted, story id: {req_body.get('story_id')}")
    except:
        return func.HttpResponse("unable to delete story, please try again.")        

def main(req: func.HttpRequest) -> func.HttpResponse:

    client = pymongo.MongoClient(CONN_STRING)

    
    try:
        client.server_info() # validate connection string
        collection = client[DB_NAME].get_collection(CONTAINER_NAME)

        return update_story(req, collection)

    except pymongo.errors.ServerSelectionTimeoutError:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
