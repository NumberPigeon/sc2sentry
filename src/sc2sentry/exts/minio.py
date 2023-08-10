from typing import Any

from miniopy_async import Minio as _Minio

from sc2sentry.config import settings


class Minio:
    """
    A thin wrapper around the Minio client that automatically load needed settings
    from settings, and create buckets in settings if they don't exist.
    """

    _instance = None

    def __init__(self):
        self.client = _Minio(
            endpoint=settings.minio.endpoint,
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key,
            session_token=settings.minio.get("session_token") or None,
            secure=settings.minio.secure,
        )

        # get some methods from the client to have a better IDE experience
        self.bucket_exists = self.client.bucket_exists
        self.make_bucket = self.client.make_bucket
        self.remove_bucket = self.client.remove_bucket
        self.list_buckets = self.client.list_buckets
        self.list_objects = self.client.list_objects
        self.get_object = self.client.get_object
        self.put_object = self.client.put_object
        self.stat_object = self.client.stat_object
        self.remove_object = self.client.remove_object
        self.presigned_get_object = self.client.presigned_get_object
        self.presigned_put_object = self.client.presigned_put_object
        self.presigned_post_policy = self.client.presigned_post_policy

    def __getattr__(self, __name: str) -> Any:
        if __name in self.__dict__:
            return self.__dict__[__name]
        else:
            return getattr(self.client, __name, None)

    @classmethod
    async def instance(cls) -> "Minio":
        if cls._instance is not None:
            return cls._instance
        instance = cls()
        cls._instance = instance
        for bucket in settings.minio.buckets:
            is_exist = await instance.client.bucket_exists(bucket)
            if not is_exist:
                await instance.client.make_bucket(bucket)
        return instance
