import random
import string

import psycopg2
import pytest
from httpx import AsyncClient

from sc2sentry.config import settings

engine = psycopg2.connect(
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
)


@pytest.fixture(scope="session")
def email():
    email = generate_random_email()
    yield email
    # 清理测试数据
    with engine.cursor() as cursor:
        cursor.execute("DELETE FROM public.user WHERE email = %s", (email,))
        engine.commit()


def generate_random_email():
    domain_length = random.randint(5, 10)  # 域名长度在 5 到 10 之间
    domain = "".join(random.choices(string.ascii_lowercase, k=domain_length))

    username_length = random.randint(5, 10)  # 用户名长度在 5 到 10 之间
    username = "".join(random.choices(string.ascii_lowercase, k=username_length))

    email = f"{username}@{domain}.com"

    # 检查email是否已经存在
    with engine.cursor() as cursor:
        cursor.execute("SELECT * FROM public.user WHERE email = %s", (email,))
        if cursor.fetchone():
            return generate_random_email()
        else:
            return email


global_token = None


# 异步测试非常复杂。目前，测试时需要手动启动服务器，然后再运行测试。
# 这似乎是一个fastapi的问题，详见：
# https://github.com/tiangolo/fastapi/issues/4473
@pytest.fixture
def test_app_url(scope="session"):
    return "http://127.0.0.1:8010"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_register(email, test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "test1",
            },
        )
    assert response.status_code == 201
    assert response.json().get("email") == email


@pytest.mark.anyio
async def test_register_duplicate(email, test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "test1",
            },
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_login(email, test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={
                "username": email,
                "password": "test1",
            },
        )
    assert response.status_code == 200
    assert response.json().get("access_token")
    global global_token
    global_token = response.json().get("access_token")


@pytest.mark.anyio
async def test_login_wrong_password(email, test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={
                "username": email,
                "password": "test2",
            },
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_login_wrong_username(test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={
                "username": "wrong_username",
                "password": "test1",
            },
        )
    assert response.status_code == 400


# NOTE: bearer + JWT 不能真的注销，只能等待 token 过期
@pytest.mark.anyio
async def test_logout(test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.post(
            "/auth/jwt/logout",
            headers={"Authorization": f"Bearer {global_token}"},
        )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_users_me(email, test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.get(
            "/auth/users/me",
            headers={"Authorization": f"Bearer {global_token}"},
        )
    assert response.status_code == 200
    assert response.json().get("email") == email


@pytest.mark.anyio
async def test_users_me_wrong_token(test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.get(
            "/auth/users/me",
        )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_users_others_info(test_app_url):
    async with AsyncClient(base_url=test_app_url) as client:
        response = await client.get(
            "/auth/users/fe07c17f-f2cb-4430-a8c4-4062d802199f",
            headers={"Authorization": f"Bearer {global_token}"},
        )
    assert response.status_code == 403


# TODO: 增加邮件相关测试用例
