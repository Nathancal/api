from distutils.log import error
import azure.functions as func
from azure.keyvault.secrets import SecretClient
from config import config
import pymongo
import uuid
import datetime

key_client = SecretClient(vault_url=config.KVUri, credential=config.credential)

CONN_STRING_KEY = config.conn_secret_key
DB_NAME = config.db_name
CONTAINER_NAME = config.container_name
CONN_STRING = key_client.get_secret(CONN_STRING_KEY)

def create_story(req: func.HttpRequest, collection) -> func.HttpResponse:
    
    story_id = uuid.uuid4().hex
    req_body = req.get_json()

    print(req_body)
    try:

        if collection.find_one({"story_id":story_id}) is None:

            collection.insert_one({
                "story_id": story_id,
                "author_id": req_body.get('user_id'),
                "title": req_body.get('title'),
                "body": req_body.get('body'),
                "created_at": datetime.datetime.utcnow(),
                "keywords": req_body.get('keywords')
            })

            return func.HttpResponse("Story successfully created")
        return func.HttpResponse("Story already exists")
    except:
        return func.HttpResponse("unable to create new story, please try again.")        

def main(req: func.HttpRequest) -> func.HttpResponse:


    
    try:
        client = pymongo.MongoClient(CONN_STRING.value)

        collection = client[DB_NAME].get_collection(CONTAINER_NAME)

        return create_story(req, collection)

    except:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
    