import json
import boto3
import base64

s3 = boto3.client('s3')

INPUT_BUCKET = 'manoj-image-input-2026'
OUTPUT_BUCKET = 'manoj-image-output-2026'

def lambda_handler(event, context):

    method = event.get("requestContext", {}) \
                  .get("http", {}) \
                  .get("method", "")

    try:

        # DOWNLOAD REQUEST
        if method == "GET":

            filename = event["queryStringParameters"]["file"]

            response = s3.head_object(
                Bucket=OUTPUT_BUCKET,
                Key=filename
            )

            compressed_size = response["ContentLength"]

            url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": OUTPUT_BUCKET,
                    "Key": filename
                },
                ExpiresIn=3600
            )

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "download_url": url,
                    "compressed_size": compressed_size
                })
            }

        # UPLOAD REQUEST
        body = json.loads(event["body"])

        image_data = base64.b64decode(body["image"])

        filename = body["filename"]

        s3.put_object(
            Bucket=INPUT_BUCKET,
            Key=filename,
            Body=image_data,
            ContentType="image/jpeg"
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "filename": filename,
                "original_size": len(image_data)
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }