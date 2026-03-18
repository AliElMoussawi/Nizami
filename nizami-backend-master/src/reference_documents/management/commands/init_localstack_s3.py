import json
import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialise S3 bucket in LocalStack for local development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete the bucket if it exists, then create a new one.",
        )

    def _empty_and_delete_bucket(self, s3_client, bucket_name: str) -> None:
        """Empty the bucket (delete all object versions) and delete the bucket."""
        paginator = s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents") or []:
                s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
        s3_client.delete_bucket(Bucket=bucket_name)
        logger.info("Deleted bucket '%s' in LocalStack.", bucket_name)

    def handle(self, *args, **options):
        force = options.get("force", False)
        if not getattr(settings, "USE_LOCALSTACK_S3", False):
            logger.info("USE_LOCALSTACK_S3 is not enabled; skipping LocalStack S3 initialisation.")
            return

        bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
        endpoint_url = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
        access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
        secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
        region_name = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")

        if not bucket_name or not endpoint_url:
            logger.info("Missing bucket name or endpoint URL; skipping LocalStack S3 initialisation.")
            return

        s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )

        try:
            existing_buckets = s3_client.list_buckets().get("Buckets", [])
            bucket_exists = any(b["Name"] == bucket_name for b in existing_buckets)

            if force and bucket_exists:
                self._empty_and_delete_bucket(s3_client, bucket_name)
                bucket_exists = False

            if not bucket_exists:
                create_params = {"Bucket": bucket_name}
                if region_name and region_name != "us-east-1":
                    create_params["CreateBucketConfiguration"] = {"LocationConstraint": region_name}
                s3_client.create_bucket(**create_params)
                logger.info("Created bucket '%s' in LocalStack.", bucket_name)
            else:
                logger.info("Bucket '%s' already exists in LocalStack.", bucket_name)

            # CORS so the browser can PUT to presigned URLs (frontend origin)
            cors = {
                "CORSRules": [
                    {
                        "AllowedHeaders": ["*"],
                        "AllowedMethods": ["GET", "PUT", "HEAD", "POST"],
                        "AllowedOrigins": [
                            "http://localhost:4200",
                            "http://localhost:4201",
                            "http://127.0.0.1:4200",
                            "http://127.0.0.1:4201",
                        ],
                        "ExposeHeaders": ["ETag"],
                    }
                ]
            }
            try:
                s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors)
                logger.info("Set CORS on bucket '%s'.", bucket_name)
            except ClientError as cors_exc:
                logger.warning("Could not set CORS on bucket '%s': %s", bucket_name, cors_exc)

            # Bucket ACL so LocalStack allows GetObject on objects uploaded via presigned PUT (local dev only).
            try:
                s3_client.put_bucket_acl(Bucket=bucket_name, ACL="public-read-write")
                logger.info("Set bucket ACL public-read-write on '%s' (local dev).", bucket_name)
            except ClientError as acl_exc:
                logger.warning("Could not set bucket ACL on '%s': %s", bucket_name, acl_exc)

            # Bucket policy so backend can GetObject/HeadObject on objects uploaded via presigned URL (local dev only).
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowBackendFullAccess",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "s3:GetObject",
                            "s3:HeadObject",
                            "s3:PutObject",
                            "s3:DeleteObject",
                            "s3:GetObjectAcl",
                            "s3:PutObjectAcl",
                        ],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                    },
                ],
            }
            try:
                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(bucket_policy),
                )
                logger.info("Set bucket policy on '%s' (local dev).", bucket_name)
            except ClientError as policy_exc:
                logger.warning("Could not set bucket policy on '%s': %s", bucket_name, policy_exc)

        except ClientError as exc:
            logger.error("Error initialising LocalStack S3 bucket '%s': %s", bucket_name, exc)

