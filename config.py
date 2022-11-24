import os

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = set(["png", "jpeg", "jpg"])
HOME_FOLDER = "_micro"
ENDPOINT_URL = "https://yourmicropubendpoint.com/micropub"
MEDIA_ENDPOINT_URL = "https://yourmicropubendpoint.com/media"

GITHUB_KEY = os.getenv("GITHUB_KEY")
ME = "gweezlebur.com"
CALLBACK_URL = "https://northern-parallel-medicine.glitch.me/micropub/callback"
CLIENT_ID = "https://micropub.gweezlebur.com"
TOKEN_ENDPOINT = "https://tokens.indieauth.com/token"
GITHUB_USER_AND_REPO = "ivey/ivey.github.com"