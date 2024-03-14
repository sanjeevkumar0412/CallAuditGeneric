import jwt
import datetime
import secrets
from ldap3 import Server, Connection, ALL, SIMPLE
from app.services.logger import Logger


class AuthenticationService:
    _instance = None

    def __init__(self):
        self.logger = Logger()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_ldap_authenticate(self, username, password):
        success = True
        error_message = None
        # Establish connection with the LDAP server
        # server_address = 'LDAP://agreeya.local/DC=agreeya,DC=local'
        server_address = 'ldap://10.9.32.17:389'
        server = Server(server_address, get_info=ALL, use_ssl=False)
        try:
            # Bind to the LDAP server with provided credentials
            conn = Connection(server, user=username, password=password, authentication=SIMPLE)
            if not conn.bind():
                success = False
                error_message = str("Invalid credentials")
                return success, error_message
            # If bind is successful, credentials are valid
            success = True
            error_message = str("Credentials verified successfully")
            return success, error_message
        except Exception as e:
            success = False
            error_message = str(e)
            # return False, f"Error: {e}"
            return success, error_message

    def ldap_authenticate_not_an_use(self, username, password):
        # Establish connection with the LDAP server
        # SERVER_ADDRESS = 'LDAP://ldap.agreeya.com/DC=agreeya,DC=com'
        SERVER_ADDRESS = 'ldap://10.9.32.17:389'
        SEARCH_BASE = "DC=agreeya,DC=local"  # Replace with your domain's search base
        conn = None
        try:
            # with Connection(SERVER_ADDRESS, user=username, password=username) as conn:
            #     if conn.bind():
            #         print("Authentication successful!")
            #     else:
            #         print("Authentication failed!")
            conn = Connection(SERVER_ADDRESS, user=username, password=password)
            if conn.bind():
                print("Authentication successful!")
            else:
                print("Authentication failed!")
        except Exception as e:
            print("Error connecting to server:", e)
        finally:
            conn.unbind()

    def get_token_based_authenticate(self, client_id, user_name):
        # Establish connection with the LDAP server
        secret_key = secrets.token_bytes(32)
        hex_key = secret_key.hex()
        print(f"Generated secret key: {hex_key}")
        SECRET_KEY = hex_key

        # Generate a JWT token with an expiry time of 1 hour
        payload = {
            'user_id': user_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print("Generated token:", token)
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print("Decoded token:", decoded_token)
            return True
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return False
        except jwt.InvalidTokenError:
            print("Invalid token")
            return False