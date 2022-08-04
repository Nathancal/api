import azure.functions as func
from azure.keyvault.secrets import SecretClient
from config import config
import pymongo
import uuid
import datetime
import jwt
import logging
import bcrypt
import re
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content



key_client = SecretClient(vault_url=config.KVUri, credential=config.credential)

CONN_STRING_KEY = config.conn_secret_key
JWT_SECRET = config.jwt_secret_key
SENDGRID_SECRET = config.sendgrid_api_key
DB_NAME = config.db_name
USERS_CONTAINER_NAME = 'users'
VERIFY_CONTAINER_NAME = 'verify'
EVENT_CONTAINER_NAME = 'event_log'
CONN_STRING = key_client.get_secret(CONN_STRING_KEY)
SENDGRID_API_KEY = key_client.get_secret(SENDGRID_SECRET)

    
def login_user(req: func.HttpRequest, collection) -> func.HttpResponse:
    
    req_body = req.get_json()
    email = req_body.get('email')

    try:

        user = collection.find_one({"email":email})

        if user is None:

            return func.HttpResponse("This user does not exist please create an account.")

              
        else:

            password = str(req_body.get('password'))

            cross_ref_pwd = bytes(user["password"], 'UTF-8')

            if bcrypt.checkpw(bytes(password, 'UTF-8'), cross_ref_pwd):

                tokenSecret = key_client.get_secret(JWT_SECRET)

                token = jwt.encode({
                        'user': email,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=int(req.form["duration"]))}
                        ,tokenSecret.value, algorithm="HS256")

                res_obj = {
                    "token": token,
                    "message": "user has been successfully logged in"
                }

                return func.HttpResponse("user with this email already exists")
            else:
                return func.HttpResponse("You have entered an incorrect password")
    except:
        return func.HttpResponse("unable to create new user, please try again.")        

def main(req: func.HttpRequest) -> func.HttpResponse:


    
    try:
        client = pymongo.MongoClient(CONN_STRING.value)

        collection = client[DB_NAME].get_collection(USERS_CONTAINER_NAME)

        return login_user(req, collection, client)

    except:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
    
   