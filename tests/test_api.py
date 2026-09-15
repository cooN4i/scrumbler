import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import Base, get_db

# Isolated in-memory async SQLite for integration tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session
        await session.commit()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_auth_and_solve_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register User
        reg_resp = await ac.post("/api/auth/register", json={
            "username": "cubemaster",
            "password": "SecretPass123!"
        })
        assert reg_resp.status_code == 201
        data = reg_resp.json()
        token = data["access_token"]
        assert token is not None

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Scramble
        scramble_resp = await ac.get("/api/solves/scramble")
        assert scramble_resp.status_code == 200
        scramble = scramble_resp.json()["scramble"]
        assert len(scramble.split()) == 21

        # 3. Save a solve (11.52 sec)
        solve_resp = await ac.post("/api/solves", headers=headers, json={
            "raw_time_ms": 11520,
            "scramble": scramble,
            "penalty": "none"
        })
        assert solve_resp.status_code == 201
        solve_data = solve_resp.json()
        solve_id = solve_data["id"]
        assert solve_data["formatted_time"] == "11.52"

        # 4. Check Stats (PB should be 11.52)
        stats_resp = await ac.get("/api/solves/stats", headers=headers)
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total_solves"] == 1
        assert stats["pb"] == "11.52"

        # 5. Apply +2 Penalty
        penalty_resp = await ac.patch(f"/api/solves/{solve_id}", headers=headers, json={
            "penalty": "+2"
        })
        assert penalty_resp.status_code == 200
        assert penalty_resp.json()["formatted_time"] == "13.52+"

        # 6. Delete solve
        del_resp = await ac.delete(f"/api/solves/{solve_id}", headers=headers)
        assert del_resp.status_code == 204

        # 7. Check stats again (0 solves)
        stats_after = await ac.get("/api/solves/stats", headers=headers)
        assert stats_after.json()["total_solves"] == 0
