from fastapi import FastAPI
from livekit import api
import os

app = FastAPI()

@app.get("/token")
def get_token(identity: str):
    token = api.AccessToken(
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET")
    ).with_identity(identity) \
     .with_grants(api.VideoGrants(room_join=True)) \
     .to_jwt()

    return {"token": token}
