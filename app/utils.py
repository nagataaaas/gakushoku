import uuid
import jwt
import datetime
from dataclasses import dataclass


@dataclass
class GoogleJwtData:
    iss: str
    azp: str
    aud: str
    sub: str
    hd: str
    email: str
    email_verified: bool
    at_hash: str
    name: str
    picture: str
    given_name: str
    family_name: str
    locale: str
    iat: int
    exp: int
    jti: str

    iat_date: datetime.datetime = None
    exp_date: datetime.datetime = None
    is_expired: bool = False


def random_uuid() -> str:
    return uuid.uuid4().hex


def decode_google_jwt(jwt_data: str) -> GoogleJwtData:
    data = jwt.decode(jwt_data.encode('utf-8'), algorithms=['RS256'], options={"verify_signature": False})
    google_data = GoogleJwtData(**data)

    google_data.iat_date, google_data.exp_date = \
        datetime.datetime.fromtimestamp(google_data.iat), datetime.datetime.fromtimestamp(google_data.exp)
    google_data.is_expired = google_data.exp_date < datetime.datetime.now()

    return google_data
