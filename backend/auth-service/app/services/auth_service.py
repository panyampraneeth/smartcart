from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse

DUMMY_HASHED_PASSWORD = "$2b$12$KIX1cFZ0ipP0bGVj0ICDeuvPhC2J/nkbcA2EvM68fUDYxWg7icj4u"

class AuthService:
    """
    Contains all business logic for authentication.
    Calls repository for database operations.
    Never writes SQL directly.
    """

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, request: RegisterRequest) -> TokenResponse:
        """
        Register a new user.
        1. Check email is not already taken
        2. Check username is not already taken
        3. Hash the password
        4. Create the user
        5. Return a JWT token
        """
        # Check email uniqueness
        existing = await self.repo.get_by_email(request.email)
        if existing:
            raise ValueError("Email already registered")

        # Check username uniqueness
        existing = await self.repo.get_by_username(request.username)
        if existing:
            raise ValueError("Username already taken")

        # Hash password — never store plain text passwords
        hashed = hash_password(request.password)

        # Create user in database
        user = await self.repo.create(
            email=request.email,
            username=request.username,
            hashed_password=hashed,
            role=request.role,
        )

        # Create JWT token
        token = create_access_token(data={"sub": str(user.id), "role": user.role})

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def login(self, request: LoginRequest) -> TokenResponse:
        """
        Login an existing user.
        1. Find user by email
        2. Verify password
        3. Return a JWT token
        """
        # Find user
        user = await self.repo.get_by_email(request.email)

        password_hash_to_check = (
            user.hashed_password
            if user
            else DUMMY_HASHED_PASSWORD
        )

        password_is_valid = verify_password(
            request.password,
            password_hash_to_check,
        )

        if not user or not password_is_valid:
            raise ValueError("Invalid email or password")

        # Check account is active
        if not user.is_active:
            raise ValueError("Account is disabled")

        # Create JWT token
        token = create_access_token(data={"sub": str(user.id), "role": user.role})

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def get_current_user(self, user_id: int) -> UserResponse:
        """Get the current logged in user's profile."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return UserResponse.model_validate(user)
