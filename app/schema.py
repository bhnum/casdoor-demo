from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_partial import create_partial_model


class Role(BaseModel):
    name: str
    display_name: Annotated[str, Field(validation_alias="displayName")]
    is_enabled: Annotated[bool, Field(validation_alias="isEnabled")]
    owner: str


class Permission(BaseModel):
    name: str
    display_name: Annotated[str, Field(validation_alias="displayName")]
    is_enabled: Annotated[bool, Field(validation_alias="isEnabled")]
    actions: list[Literal["Read", "Write", "Admin"]]
    resource_type: Annotated[
        Literal["Application", "TreeNode", "Custom"],
        Field(validation_alias="resourceType"),
    ]
    resources: list[str]
    effect: Literal["Allow", "Deny"]
    owner: str


class User(BaseModel):
    id: str
    username: Annotated[str, Field(validation_alias="name")]
    display_name: Annotated[str, Field(validation_alias="displayName")]
    email: str
    phone: str
    avatar: str
    roles: list[Role]
    permissions: list[Permission]
    groups: list[str]
    owner: str


class BookRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    author: str
    creator_user_id: str
    modifier_user_id: str
    created: datetime
    updated: datetime


class BookSummaryRes(BookRes):
    pass


class BookDetailsRes(BookRes):
    content: str


class BookReq(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    author: str
    content: str


BookReqPartial = create_partial_model(BookReq)
