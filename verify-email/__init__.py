import azure.functions as func
from azure.keyvault.secrets import SecretClient
from config import config
import pymongo




key_client = SecretClient(vault_url=config.KVUri, credential=config.credential)

CONN_STRING_KEY = config.conn_secret_key
JWT_SECRET = config.jwt_secret_key
DB_NAME = config.db_name
CONTAINER_NAME = 'users'
CONN_STRING = key_client.get_secret(CONN_STRING_KEY)

def verify_email(req: func.HttpRequest, collection) -> func.HttpResponse:
    
    user_id = req.route_params.get('user_id')
    
    try:

        if collection.find_one({"user_id":user_id}) is None:

            return func.HttpResponse("This user does not exist.")
        else:

            collection.update_one({
                "user_id": user_id
            },{"$set": {"email_verified": True}})

            return func.HttpResponse("email address has been verified.")
    except:
        return func.HttpResponse("unable to verify email address, please try again.")        

def main(req: func.HttpRequest) -> func.HttpResponse:


    
    try:
        client = pymongo.MongoClient(CONN_STRING.value)

        collection = client[DB_NAME].get_collection(CONTAINER_NAME)

        return verify_email(req, collection)

    except:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
    
   

