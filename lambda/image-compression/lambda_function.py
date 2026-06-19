import boto3
from PIL import Image
import os
import urllib.parse

s3 = boto3.client('s3')

OUTPUT_BUCKET = 'manoj-image-output-2026'

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key']
    )

    download_path = '/tmp/' + os.path.basename(key)
    upload_path = '/tmp/resized-' + os.path.basename(key)

    s3.download_file(bucket, key, download_path)

    image = Image.open(download_path)
    image.thumbnail((300,300))
    image.save(upload_path)

    s3.upload_file(
        upload_path,
        OUTPUT_BUCKET,
        'resized-' + os.path.basename(key)
    )

    return {
        'statusCode': 200,
        'body': 'Image resized successfully'
    }
