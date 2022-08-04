import msal
from azure.identity import DefaultAzureCredential
import os

class config():
    KVUri = f"https://ncportfoliokeys.vault.azure.net/"
    credential = DefaultAzureCredential()
    conn_secret_key = "CONNSTRING"
    db_name = "portfolio"
    client_secret = "ey38Q~fKL8xeiDXQ4UhEFbSt7IwLzSMuURumdckM"