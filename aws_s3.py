import boto3

# Initialize S3 client
s3_client = boto3.client('s3')

# Define bucket name and file details
bucket_name = "logbooks"
file_to_upload = "/Users/lauraboelsterli/Downloads/mars.pdf"  # Replace with your file path
object_name = "mars.pdf"

# Define custom metadata
metadata = {
    "title": "The Outlook on Mars",
    "subject": "Mars",
    "description": (
        "Percival Lowell's article 'Is There Life on Mars' in Outlook Magazine"),
    "creator": "Lowell, Percival",
    "date": "1907-02",
    "rights": "This object is property of the Lowell Observatory Archives. Any public use requires the written permission of the Lowell Observatory Archives. Contact us at archives@lowell.edu",
    "format": "Handwritten document, Typed document",
    "language": "English",
    "type": "Text",
    "identifier": "mars"
}

# Upload the file to S3 with metadata
try:
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=open(file_to_upload, "rb"),
        Metadata=metadata
    )
    print(f"File {object_name} uploaded successfully to {bucket_name} with metadata.")
except Exception as e:
    print(f"Error uploading file: {e}")
