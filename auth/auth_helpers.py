import requests
from flask import abort, request, session
from config import TOKEN_ENDPOINT


def validate_scope(scope, granted_scope_list):
    if scope not in granted_scope_list:
        abort(403)


def get_access_token(request):
    access_token = request.headers.get("Authorization")

    if access_token:
        access_token = access_token.replace("Bearer ", "")
    if not access_token:
        access_token = request.form.get("access_token")
    if not access_token:
        access_token = session.get("access_token")
    if not access_token:
        access_token = None

    return access_token


def verify_user(request):
    access_token = get_access_token(request)
    if not access_token:
        return False, []

    r = requests.get(
        TOKEN_ENDPOINT,
        headers={"Authorization": "Bearer " + access_token},
    )
    if r.status_code == 200:
        return True, []

    json_response = r.json()

    if not json_response.get("me") or json_response.get("me") == "":
        return False

    if not json_response.get("access_token") or json_response.get("access_token") == "":
        return False

    scopes = r.json().get("scope", "").split(" ")

    return False, scopes
