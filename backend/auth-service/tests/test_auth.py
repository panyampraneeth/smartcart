import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "@localhost:5433/smartcart",
    "@localhost:5433/smartcart_test"
)
from sqlalchemy.pool import NullPool

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = override_get_db

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    app.dependency_overrides.clear()

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

async def test_health_check(client):
    response = await client.get("/auth/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

async def test_register_success(client):
    response = await client.post("/auth/register", json={
        "email": "test@smartcart.com",
        "username": "testuser",
        "password": "password123",
        "role": "buyer"
    })

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@smartcart.com"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["role"] == "buyer"
    assert "hashed_password" not in data["user"]

async def test_register_duplicate_email(client):
    payload = {
        "email": "test@smartcart.com",
        "username": "testuser",
        "password": "password123",
        "role": "buyer"
    }

    await client.post("/auth/register", json=payload)

    response = await client.post("/auth/register", json={
        **payload,
        "username": "differentuser"
    })

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "test@smartcart.com",
        "username": "testuser",
        "password": "password123",
        "role": "buyer"
    })

    response = await client.post("/auth/login", json={
        "email": "test@smartcart.com",
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@smartcart.com"

async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "test@smartcart.com",
        "username": "testuser",
        "password": "password123",
        "role": "buyer"
    })

    response = await client.post("/auth/login", json={
        "email": "test@smartcart.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

async def test_login_nonexistent_email(client):
    response = await client.post("/auth/login", json={
        "email": "nobody@smartcart.com",
        "password": "password123"
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

async def test_register_invalid_email(client):
    response = await client.post("/auth/register", json={
        "email": "notanemail",
        "username": "testuser",
        "password": "password123",
        "role": "buyer"
    })

    assert response.status_code == 422