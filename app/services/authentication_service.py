import jwt
import datetime
import secrets
from ldap3 import Server, Connection, ALL, SIMPLE, NTLM, core
class AuthenticationService:

    def get_ldap_authenticate(self, username, password):
        # Establish connection with the LDAP server
        # server_address = 'LDAP://agreeya.local/DC=agreeya,DC=local'
        server_address = 'ldap://10.9.32.17:389'
        server = Server(server_address, get_info=ALL, use_ssl=False)
        try:
            # Bind to the LDAP server with provided credentials
            conn = Connection(server, user=username, password=password, authentication=SIMPLE)
            if not conn.bind():
                return False, "Invalid credentials"
            # If bind is successful, credentials are valid
            return True, "Credentials verified successfully"
        except Exception as e:
            # return False, f"Error: {e}"
            return False

    def ldap_authenticate(self, username, password):
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

    def get_token_based_authenticate(self, username):
        # Establish connection with the LDAP server
        secret_key = secrets.token_bytes(32)
        hex_key = secret_key.hex()
        print(f"Generated secret key: {hex_key}")
        SECRET_KEY = hex_key

        # Generate a JWT token with an expiry time of 1 hour
        payload = {
            'user_id': username,
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