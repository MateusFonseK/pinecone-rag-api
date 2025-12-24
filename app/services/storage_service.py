import boto3
from botocore.config import Config
from app.config import settings


_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.r2_access_key_id,
    aws_secret_access_key=settings.r2_secret_access_key,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

_bucket = settings.r2_bucket_name


def upload_file(file_path: str, filename: str) -> None:
    """Upload a file to R2."""
    _client.upload_file(file_path, _bucket, filename)


def download_file(filename: str, destination: str) -> None:
    """Download a file from R2."""
    _client.download_file(_bucket, filename, destination)


def delete_file(filename: str) -> None:
    """Delete a file from R2."""
    _client.delete_object(Bucket=_bucket, Key=filename)


def file_exists(filename: str) -> bool:
    """Check if a file exists in R2."""
    try:
        _client.head_object(Bucket=_bucket, Key=filename)
        return True
    except _client.exceptions.ClientError:
        return False


def get_file_size(filename: str) -> int:
    """Get file size in bytes."""
    response = _client.head_object(Bucket=_bucket, Key=filename)
    return response["ContentLength"]


def list_files() -> list[dict]:
    """List all files in the bucket."""
    response = _client.list_objects_v2(Bucket=_bucket)
    files = []

    for obj in response.get("Contents", []):
        files.append({
            "filename": obj["Key"],
            "size_bytes": obj["Size"],
        })

    return files


def get_file_stream(filename: str):
    """Get a file stream for downloading."""
    response = _client.get_object(Bucket=_bucket, Key=filename)
    return response["Body"]
