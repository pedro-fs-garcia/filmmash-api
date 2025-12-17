from pydantic import BaseModel


class UserCreatedResponse(BaseModel):
    id: str
    email: str
    username: str
    access_token: str
    refresh_token: str


class RefreshSessionRequest(BaseModel):
    refresh_token: str


class RefreshSessionResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class RegisterUserRequest(BaseModel):
    email: str
    username: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str
