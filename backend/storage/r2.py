from __future__ import annotations

import os
from pathlib import Path

import boto3
from mypy_boto3_s3 import S3Client


class R2StorageClient:
    def __init__(
        self,
        *,
        bucket: str | None = None,
        endpoint: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
    ) -> None:
        self._bucket = bucket or os.getenv("R2_BUCKET") or ""

        resolved_endpoint = endpoint or os.getenv("R2_ENDPOINT") or ""

        resolved_access_key = access_key_id or os.getenv("R2_ACCESS_KEY_ID") or ""

        resolved_secret_key = (
            secret_access_key or os.getenv("R2_SECRET_ACCESS_KEY") or ""
        )

        if not self._bucket:
            raise RuntimeError("R2_BUCKET is not configured")

        if not resolved_endpoint:
            raise RuntimeError("R2_ENDPOINT is not configured")

        if not resolved_access_key:
            raise RuntimeError("R2_ACCESS_KEY_ID is not configured")

        if not resolved_secret_key:
            raise RuntimeError("R2_SECRET_ACCESS_KEY is not configured")

        self._client: S3Client = boto3.client(
            service_name="s3",
            endpoint_url=resolved_endpoint,
            aws_access_key_id=resolved_access_key,
            aws_secret_access_key=resolved_secret_key,
            region_name="auto",
        )

    @property
    def bucket(self) -> str:
        return self._bucket

    def upload_bytes(
        self,
        *,
        storage_key: str,
        content: bytes,
        content_type: str | None = None,
    ) -> None:
        if content_type:
            self._client.put_object(
                Bucket=self._bucket,
                Key=storage_key,
                Body=content,
                ContentType=content_type,
            )
        else:
            self._client.put_object(
                Bucket=self._bucket,
                Key=storage_key,
                Body=content,
            )

    def upload_file(
        self,
        *,
        storage_key: str,
        path: Path,
        content_type: str | None = None,
    ) -> None:
        extra_args = {}

        if content_type:
            extra_args["ContentType"] = content_type

        self._client.upload_file(
            str(path),
            self._bucket,
            storage_key,
            ExtraArgs=(extra_args if extra_args else None),
        )

    def download_file(
        self,
        *,
        storage_key: str,
        destination: Path,
    ) -> Path:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._client.download_file(
            self._bucket,
            storage_key,
            str(destination),
        )

        return destination

    def delete(
        self,
        *,
        storage_key: str,
    ) -> None:
        self._client.delete_object(
            Bucket=self._bucket,
            Key=storage_key,
        )

    def exists(
        self,
        *,
        storage_key: str,
    ) -> bool:
        try:
            self._client.head_object(
                Bucket=self._bucket,
                Key=storage_key,
            )

            return True
        except self._client.exceptions.ClientError as exc:
            response = exc.response

            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

            if status == 404:
                return False

            raise
