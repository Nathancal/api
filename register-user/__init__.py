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

def verify_initiate(req: func.HttpRequest, client: pymongo.MongoClient, user_id) -> func.HttpResponse:
    
    req_body = req.get_json()
    email = req_body.get('email')
    forename = req_body.get('forename')
                
    verify_email_coll = client[DB_NAME].get_collection(VERIFY_CONTAINER_NAME)
    event_log_coll = client[DB_NAME].get_collection(EVENT_CONTAINER_NAME)

    verify_session = uuid.uuid4().hex
    try:
        verify_email_coll.insert_one({
            "verify_session_id": verify_session,
            "email": email,
            "created_at": datetime.datetime.utcnow(),
            "verify_complete": False 
        })
      
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

        from_email = Email("Callaghan-n6@ulster.ac.uk")
        to_email = To(email)
        subject = f"Verify Email address, {forename}"
        content = Content("text/plain", f"this is a test email to verify an account details are {user_id}/{verify_session}")

        mail = Mail(from_email, to_email, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()
        response = sg.send(request_body=mail_json)
        logging.info(response)
        print(response.status_code)
        print(response.headers)
        return func.HttpResponse("user successfully created, please verify email to access account.")

    except:
        return func.HttpResponse("Unable to create session_verify object try again.")




def register_user(req: func.HttpRequest, collection, client: pymongo.MongoClient) -> func.HttpResponse:
    
    user_id = uuid.uuid4().hex
    req_body = req.get_json()
    email = req_body.get('email')

    try:
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):

            if collection.find_one({"email":email}) is None:

                password = str(req_body.get('password'))

                hash = str(bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=10)))
                splitHash = hash.split("'", 3)

                collection.insert_one({
                    "user_id": user_id,
                    "email": email,
                    "password": str(splitHash[1]),
                    "created_at": datetime.datetime.utcnow(),
                    "user_type": req_body.get('user_type'),
                    "forename": req_body.get('forename'),
                    "surname": req_body.get('surname'),
                    "bio": req_body.get('user_bio'),
                    "email_verified": False
                })

                verify_initiate(req, client, user_id)

                return func.HttpResponse("user successfully created, please verify email to access account.")
            else:
                return func.HttpResponse("user with this email already exists")
        else:
            return func.HttpResponse("email address is not valid.")
    except:
        return func.HttpResponse("unable to create new user, please try again.")        

def main(req: func.HttpRequest) -> func.HttpResponse:


    
    try:
        client = pymongo.MongoClient(CONN_STRING.value)

        collection = client[DB_NAME].get_collection(USERS_CONTAINER_NAME)

        return register_user(req, collection, client)

    except:
        return func.HttpResponse("Invalid API for MongoDB connection string or timed out when attempting to connect")
    
   
