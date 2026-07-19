import boto3
from PIL import Image, ImageOps
import os
import urllib.parse

s3 = boto3.client("s3")

OUTPUT_BUCKET = "manoj-image-output-2026"


def lambda_handler(event, context):

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    filename = os.path.basename(key)

    download_path = f"/tmp/{filename}"
    upload_path = f"/tmp/resized-{filename}"

    # Download image
    s3.download_file(bucket, key, download_path)

    image = Image.open(download_path)

    # Correct orientation using EXIF
    image = ImageOps.exif_transpose(image)

    # Resize only if image is huge
    MAX_SIZE = (1920, 1920)
    image.thumbnail(MAX_SIZE)

    image_format = image.format

    save_kwargs = {}

    if image_format in ["JPEG", "JPG"]:

        if image.mode != "RGB":
            image = image.convert("RGB")

        save_kwargs = {
            "format": "JPEG",
            "quality": 70,
            "optimize": True,
            "progressive": True
        }

    elif image_format == "PNG":

        save_kwargs = {
            "format": "PNG",
            "optimize": True,
            "compress_level": 9
        }

    elif image_format == "WEBP":

        save_kwargs = {
            "format": "WEBP",
            "quality": 70,
            "method": 6
        }

    elif image_format == "GIF":

        save_kwargs = {
            "format": "GIF",
            "optimize": True
        }

    else:
        image.save(upload_path)
        s3.upload_file(
            upload_path,
            OUTPUT_BUCKET,
            f"resized-{filename}"
        )

        return {
            "statusCode": 200,
            "body": "Uploaded (unsupported compression format)"
        }

    image.save(upload_path, **save_kwargs)

    s3.upload_file(
        upload_path,
        OUTPUT_BUCKET,
        f"resized-{filename}"
    )

    return {
        "statusCode": 200,
        "body": "Image compressed successfully"
    }