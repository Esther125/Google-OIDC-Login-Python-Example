import os
import requests
from google_auth_oauthlib.flow import Flow


class OIDCService:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        self.flow = Flow.from_client_secrets_file(
            "client.json",
            scopes=[
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "openid",
            ],
            redirect_uri=self.redirect_uri,
        )
    
    def get_auth_server_url(self):
        authorization_url, state = self.flow.authorization_url()
        return authorization_url, state

    def authorize(self, authorization_response):
        token_info = self.flow.fetch_token(
            authorization_response=authorization_response
        )
        access_token = self.flow.credentials.token
        userinfo_response = requests.get(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        userinfo = userinfo_response.json()
        return token_info, access_token, userinfo
