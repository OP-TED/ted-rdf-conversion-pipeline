import io
import os
import ssl
from datetime import timedelta

import certifi
import urllib3
from minio import Minio
from urllib3.response import HTTPResponse

from ted_sws import config
from ted_sws.notice_publisher.model.s3_publish_result import S3PublishResult

DEFAULT_S3_OBJECT_CONTENT_TYPE = "application/octet-stream"
DEFAULT_S3_RDF_CONTENT_TYPE = "text/plain; charset=utf-8"


class S3Publisher:
    """
    This adapter is to be used to interact with triple store server on S3 bucket.
    """

    def __init__(self, host: str = config.S3_PUBLISH_HOST,
                 user: str = config.S3_PUBLISH_USER,
                 password: str = config.S3_PUBLISH_PASSWORD,
                 secure: bool = config.S3_PUBLISH_SECURE,
                 region: str = config.S3_PUBLISH_REGION,
                 ssl_verify: bool = config.S3_PUBLISH_SSL_VERIFY):

        if ssl_verify:
            self.client = Minio(
                host,
                access_key=user,
                secret_key=password,
                secure=secure,
                region=region
            )
        else:
            urllib3.disable_warnings()
            timeout = timedelta(minutes=5).seconds
            self.client = Minio(
                host,
                access_key=user,
                secret_key=password,
                secure=secure,
                region=region,
                http_client=urllib3.PoolManager(
                    timeout=urllib3.util.Timeout(connect=timeout, read=timeout),
                    maxsize=10,
                    cert_reqs=ssl.CERT_NONE,
                    ca_certs=os.environ.get('SSL_CERT_FILE') or certifi.where(),
                    retries=urllib3.Retry(
                        total=5,
                        backoff_factor=0.2,
                        status_forcelist=[500, 502, 503, 504]
                    )
                )
            )

    def create_bucket_if_not_exists(self, bucket_name: str):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def publish(self, bucket_name: str, object_name: str, data: bytes, metadata: dict = None,
                content_type=DEFAULT_S3_OBJECT_CONTENT_TYPE) -> S3PublishResult:
        self.create_bucket_if_not_exists(bucket_name)

        result = self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=io.BytesIO(data),
            length=len(data),
            metadata=(metadata or {}),
            content_type=content_type
        )
        return result

    def rdf_bucket_policy(self, bucket_name: str):
        return self.bucket_public_policy(bucket_name)

    def bucket_public_policy(self, bucket_name: str):
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": "arn:aws:s3:::" + bucket_name,
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::" + bucket_name + "/*",
                },
            ],
        }

    def is_published(self, bucket_name: str, object_name: str, version_id=None) -> bool:
        try:
            response: HTTPResponse = self.client.get_object(bucket_name=bucket_name, object_name=object_name,
                                                            version_id=version_id)
            response_status = response.status
            response.close()
            response.release_conn()

            return response_status == 200
        except Exception:
            return False

    def remove_object(self, bucket_name: str, object_name: str, version_id=None):
        self.client.remove_object(bucket_name, object_name, version_id)

    def remove_bucket(self, bucket_name: str):
        self.client.remove_bucket(bucket_name)
