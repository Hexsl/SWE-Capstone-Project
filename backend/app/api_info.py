from rest_framework.decorators import api_view
from rest_framework.response import Response

from database import queries
from database.db import get_db


@api_view(["GET"])
def emergency(request):
    """GET /api/emergency/  - public help numbers (911, police, MTA Police, ...), in display order."""
    data = queries.emergency_info(get_db())
    return Response({"items": [{"key": i.get("key"), "name": i.get("name"), "category": i.get("category"),
                                "phone": i.get("phone"), "sms": i.get("sms"), "url": i.get("url"),
                                "when_to_use": i.get("when_to_use", "")} for i in data["items"]],
                     "updated_at": data["updated_at"]})
