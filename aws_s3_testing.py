import boto3

# Initialize S3 client
s3_client = boto3.client('s3')

# Define bucket name and object name
bucket_name = "logbooks"  # Replace with your bucket name
object_name = "1976.pdf.pdf"  # Replace with your object key

# Fetch and print metadata
try:
    response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
    metadata = response.get("Metadata", {})
    print("Extracted Metadata:", metadata)
except Exception as e:
    print(f"Error fetching metadata: {e}")

