from pydantic import BaseModel, Field

class UserRegisterSchema(BaseModel):
    """
    Schema for user signup requests.
    """
    name: str = Field(..., min_length=2, example="John Doe")
    email: str = Field(..., min_length=3, example="john@company.com")
    password: str = Field(..., min_length=6, example="secure123")

class UserLoginSchema(BaseModel):
    """
    Schema for user signin requests.
    """
    email: str = Field(..., min_length=3, example="john@company.com")
    password: str = Field(..., min_length=6, example="secure123")

class ForgotPasswordSchema(BaseModel):
    """
    Schema for password reset/forgotten requests.
    """
    email: str = Field(..., min_length=3, example="john@company.com")

class UserResponseSchema(BaseModel):
    """
    Schema for representing a user profile in API responses.
    """
    id: str
    name: str
    email: str
    role: str = "Administrator"

    class Config:
        from_attributes = True

class AuthResponseSchema(BaseModel):
    """
    Schema returned upon successful signup or login.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema
