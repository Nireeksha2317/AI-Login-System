from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class SignUpRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Username must contain at least 3 characters."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        requirements = {
    "8 characters": len(value) >= 8,
    "lowercase letter": any(character.islower() for character in value),
    "uppercase letter": any(character.isupper() for character in value),
    "number": any(character.isdigit() for character in value),
    "special character": any(not character.isalnum() for character in value),
    }
        missing = [
            name
            for name, satisfied in requirements.items()
            if not satisfied
        ]

        if missing:
            raise ValueError(
                "Password must satisfy: "
                + ", ".join(missing)
                + "."
            )

        return value

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(
        cls,
        value: str,
    ) -> str:
        return value

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError(
                "Passwords do not match."
            )

        return self


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True,
    }

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse