from typing import Annotated

from casdoor import CasdoorSDK
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.config import settings
from app.schema import User

casdoor_sdk = CasdoorSDK(
    endpoint=str(settings.AUTH_ENDPOINT_URL).rstrip("/"),
    client_id=settings.AUTH_CLIENT_ID,
    client_secret=settings.AUTH_CLIENT_SECRET.get_secret_value(),
    certificate=settings.auth_public_key,
    application_name="demo-app",
    org_name=None,
)


def get_login_url():
    from requests import PreparedRequest

    url = str(settings.AUTH_FRONT_ENDPOINT_URL) + "login/oauth/authorize"
    params = {
        "client_id": casdoor_sdk.client_id,
        "response_type": "code",
        "redirect_uri": settings.AUTH_CALLBACK_URL,
        "scope": "read",
        "state": casdoor_sdk.application_name,
    }
    req = PreparedRequest()
    req.prepare_url(url, params)
    return req.url


token_bearer = HTTPBearer(
    bearerFormat="JWT",
    description=f'<b><a href="{get_login_url()}" target="_blank">Login here</a></b> and enter the access token.<br/>For the front-end application the redirect_uri query parameter should be changed.',
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
        user = casdoor_sdk.parse_jwt_token(creds.credentials)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    return User.model_validate(user)


def authorize(roles: list[str] = [], permissions: list[str] = []):
    # A very basic authorization, TODO: use casbin instead
    def check_user(user: Annotated[User, Depends(get_current_user)]):
        if all(
            any(
                user_role.name == role and user_role.is_enabled
                for user_role in user.roles
            )
            for role in roles
        ) and all(
            any(
                user_perm.name == perm and user_perm.is_enabled
                for user_perm in user.permissions
            )
            for perm in permissions
        ):
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient access",
        )

    return check_user
