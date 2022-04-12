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

