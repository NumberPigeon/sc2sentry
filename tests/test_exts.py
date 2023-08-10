import uuid
from io import BytesIO

import pytest
from miniopy_async.error import S3Error

from sc2sentry.config import settings
from sc2sentry.exts import Minio


@pytest.fixture
def anyio_backend(scope="module"):
    return "asyncio"


buckets = []


# region minio
@pytest.fixture
@pytest.mark.anyio
async def minio(scope="module"):
    minio = await Minio.instance()
    # record current buckets
    yield minio
    # remove buckets created during test
    # for bucket in await minio.list_buckets():
    #     if bucket not in prev_buckets:
    #         await minio.remove_bucket(bucket.name)
    #
    # The code above may cause error in situation that:
    # during test. a bucket is created by other process,
    # and will be removed by this code.
    # Temporary solution is to record all buckets created during test
    # using a global variable.
    global buckets
    for bucket in buckets:
        if await minio.bucket_exists(bucket):
            # delete all objects in bucket
            objects = await minio.list_objects(bucket)
            for obj in objects:
                await minio.remove_object(bucket, obj.object_name)
            await minio.remove_bucket(bucket)


# test if all buckets in settings are created
@pytest.mark.anyio
async def test_minio_buckets(minio: Minio):
    for bucket in settings.minio.buckets:
        is_exist = await minio.bucket_exists(bucket)
        assert is_exist


# test create bucket
@pytest.mark.anyio
async def test_minio_create_bucket(minio: Minio):
    bucket = str(uuid.uuid4())
    global buckets
    buckets.append(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert not is_exist
    await minio.make_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist


# test remove bucket
@pytest.mark.anyio
async def test_minio_remove_bucket(minio: Minio):
    bucket = str(uuid.uuid4())
    global buckets
    buckets.append(bucket)
    await minio.make_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    await minio.remove_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert not is_exist


# test list buckets
@pytest.mark.anyio
async def test_minio_list_buckets(minio: Minio):
    buckets = await minio.list_buckets()
    assert isinstance(buckets, list)


# test put object
@pytest.mark.anyio
async def test_minio_put_object(minio: Minio):
    bucket = str(uuid.uuid4())
    global buckets
    buckets.append(bucket)
    await minio.make_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    object_name = str(uuid.uuid4())
    data = b"hello world"
    await minio.put_object(bucket, object_name, BytesIO(data), len(data))
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    is_exist = await minio.stat_object(bucket, object_name)
    assert is_exist


# test get object
@pytest.mark.anyio
async def test_minio_get_object(minio: Minio):
    bucket = str(uuid.uuid4())
    global buckets
    buckets.append(bucket)
    await minio.make_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    object_name = str(uuid.uuid4())
    data = b"hello world"
    await minio.put_object(bucket, object_name, BytesIO(data), len(data))
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    response = await minio.get_object(bucket, object_name, None)
    data = await response.read()
    assert data == b"hello world"


# test remove object
@pytest.mark.anyio
async def test_minio_remove_object(minio: Minio):
    bucket = str(uuid.uuid4())
    global buckets
    buckets.append(bucket)
    await minio.make_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    object_name = str(uuid.uuid4())
    data = b"hello world"
    await minio.put_object(bucket, object_name, BytesIO(data), len(data))
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    is_exist = await minio.stat_object(bucket, object_name)
    assert is_exist
    await minio.remove_object(bucket, object_name)
    with pytest.raises(S3Error):
        await minio.stat_object(bucket, object_name)


# test list objects
@pytest.mark.anyio
async def test_minio_list_objects(minio: Minio):
    bucket = str(uuid.uuid4())
    global buckets
    buckets.append(bucket)
    await minio.make_bucket(bucket)
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    object_name = str(uuid.uuid4())
    data = b"hello world"
    await minio.put_object(bucket, object_name, BytesIO(data), len(data))
    is_exist = await minio.bucket_exists(bucket)
    assert is_exist
    objects = await minio.list_objects(bucket)
    assert isinstance(objects, list)
    assert len(objects) == 1
    assert objects[0].object_name == object_name


# endregion
