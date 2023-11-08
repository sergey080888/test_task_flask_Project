import time
from typing import Any
from bson.errors import InvalidId
from pydantic import BaseModel, ValidationError, field_validator, Field
from bson import ObjectId
from key import Key


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


class CreateNotification(BaseModel):
    user_id: str | None = None
    key: str
    target_id: str | None = None
    data: Any | None = None
    is_new: bool
    timestamp: int | int = Field(default_factory=lambda: int(time.time()))

    @field_validator('key')
    @classmethod
    def check_key(cls, v: str) -> str:
        if not hasattr(Key, v):
            raise HttpError(status_code=400, message=f'{v} не является ключем класса Key')
        return v

    @field_validator('user_id', 'target_id')
    @classmethod
    def check_user_id(cls, v: str) -> ObjectId:
        try:
            v = ObjectId(v)
            return v
        except InvalidId as e:
            error_message = repr(e)
            raise HttpError(status_code=400, message=error_message)


def validation_create_notification(json_data):
    try:
        ad_schema = CreateNotification(**json_data)
        return ad_schema.model_dump(exclude_none=True)

    except ValidationError as er:
        raise HttpError(status_code=400, message=er.errors())


class ListNotification(BaseModel):
    user_id: str | None = None
    limit: int | None = None
    skip: int | None = None

    @field_validator('user_id')
    @classmethod
    def check_user_id(cls, v: str):
        return CreateNotification.check_user_id(v)

    @field_validator('limit', 'skip')
    @classmethod
    def check_int(cls, v: int):
        try:
            return int(v)
        except ValueError as er:
            raise HttpError(status_code=400, message=f'{er}')


def validation_list_notification(json_data):
    try:
        ad_schema = ListNotification(**json_data)
        return ad_schema.model_dump(exclude_none=True)

    except ValidationError as er:
        raise HttpError(status_code=400, message=er.errors())


class CreateReadMark(BaseModel):
    user_id: str
    notification_id: str

    @field_validator('user_id', 'notification_id')
    @classmethod
    def check_user_str(cls, v: str):
        try:
            ObjectId(v)
            return v

        except InvalidId as e:
            error_message = repr(e)
            raise HttpError(status_code=400, message=error_message)


def create_mark(json_data):
    try:
        schema = dict(CreateReadMark(**json_data))
        ad_schema = {key: ObjectId(value) for (key, value) in schema.items() if schema.get(key)}
        del schema
        return ad_schema
    except ValidationError as er:
        raise HttpError(status_code=400, message=er.errors())
