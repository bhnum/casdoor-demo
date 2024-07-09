from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.casdoor import Casdoor
from app.config import settings
from app.schema import User

casdoor = Casdoor(
    endpoint=str(settings.AUTH_ENDPOINT_URL).rstrip("/"),
    front_endpoint=str(settings.AUTH_FRONT_ENDPOINT_URL).rstrip("/"),
    client_id=settings.AUTH_CLIENT_ID,
    client_secret=settings.AUTH_CLIENT_SECRET.get_secret_value(),
    certificate=settings.auth_public_key,
    application_name="demo-app",
    org_name=None,
)

token_bearer = HTTPBearer(
    bearerFormat="JWT",
    description=f'<b><a href="{casdoor.get_auth_link(str(settings.AUTH_CALLBACK_URL))}" target="_blank">Login here</a></b> and enter the access token.<br/>For the front-end application the redirect_uri query parameter should be changed.',
    auto_error=False,
)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(token_bearer)],
):
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = casdoor.parse_jwt_token(creds.credentials)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    return User.model_validate(user)


def authorize(obj: str, acts: list[str] = []):
    async def check_user(user: Annotated[User, Depends(get_current_user)]):
        rules = [[user.id, obj, act] for act in acts]
        authorized = await casdoor.batch_enforce("uc-model", rules)

        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient access",
            )

        return user

    return check_user
