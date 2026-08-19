import datetime
from pydantic import BaseModel, ConfigDict

class UserCreateSchema(BaseModel):
    name: str
    email: str
    phone: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    subscription: str | None = None
    subscription_expiry: datetime.datetime | None = None
    credits: int
    credits_reset_at: datetime.datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponseSchema(BaseModel):
    user: UserResponseSchema
    token: str

    model_config = ConfigDict(from_attributes=True)


class ContinueWithGoogleSchema(BaseModel):
    # ID token obtained from Google (recommended flow: client gets id_token and sends to backend)
    id_token: str | None = None
    email: str | None = None
    name: str | None = None
    google_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PasswordSchema(BaseModel):
    password: str


class UpdatePasswordSchema(BaseModel):
    new_password: str


class VerifyOTPSchema(BaseModel):
    email: str
    otp: str


class SupportRequestSchema(BaseModel):
    email: str
    category: str
    details: str
