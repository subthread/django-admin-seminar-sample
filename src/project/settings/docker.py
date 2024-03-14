# Docker環境固有の設定

from .base import *

DEBUG = True  # base.py がどうなっていようと DEBUG=True にする

# localstack を使う
AWS_ACCESS_KEY_ID = "localstack"
AWS_SECRET_ACCESS_KEY = "localstack_secret"
AWS_S3_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")


# STORAGES 調整
def __fix_storage_access(storage):
    options = storage.get("OPTIONS")
    if storage.get("BACKEND") == "storages.backends.s3boto3.S3Boto3Storage" and options:
        # node-proxy 経由で 80ポートを使ってアクセスする設定
        storage["OPTIONS"] = {
            **options,
            "url_protocol": "http:",
            "custom_domain": f"{SERVER_DOMAIN}/{options.get('bucket_name')}",
        }


__fix_storage_access(STORAGES["resource"])
