from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from database import accounts
from database.db import get_db


class MongoUser:
    """Minimal stand-in for a Django user, wrapping the MongoDB user document."""
    is_authenticated = True

    def __init__(self, doc):
        self.doc = doc
        self.id = str(doc["_id"])


class MongoSessionAuthentication(BaseAuthentication):
    """Reads 'Authorization: Bearer <token>' and looks the user up in the MongoDB sessions."""

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header or header[0].lower() != b"bearer":
            return None
        if len(header) != 2:
            raise AuthenticationFailed("Invalid token header.")
        token = header[1].decode()
        doc = accounts.user_from_session(get_db(), token)
        if not doc:
            raise AuthenticationFailed("Session expired. Please log in again.")
        return (MongoUser(doc), token)

    def authenticate_header(self, request):
        return "Bearer"