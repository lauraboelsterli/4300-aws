'''this works! has old search index prompt for terms and summary'''
import boto3
import pymysql
import requests
import os
import json
from chat_api import OpenAI 
import fitz  

# # Initialize AWS clients
s3_client = boto3.client('s3')
db_connection = None
openai_api = OpenAI()

def connect_to_rds():
    """Establish a connection to the RDS instance."""
    global db_connection
    if not db_connection:
        db_connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=3306
        )
    return db_connection

def process_pdf(file_content, catalog_metadata, limit=None):
    """Extract text from a PDF and call the OpenAI API."""
    pdf = fitz.open(stream=file_content, filetype="pdf")
    extracted_data = []
    catalog_id = catalog_metadata.get('identifier', 'Unknown identifier')
    for page_num in range(pdf.page_count):
        if page_num == limit:
            break 
        page = pdf[page_num]

        system_content = f"""
        You are a helpful assistant analyzing and extracting information from historical astronomy documents.
        This document is part of a catalog titled "{catalog_metadata.get('title', 'Unknown Title')}" and is a 
        {catalog_metadata.get('format', 'Unknown Format')} of {catalog_metadata.get('type', 'Unknown Type')} in {catalog_metadata.get('language', 'Unknown Language')},
        created by {catalog_metadata.get('creator', 'an unknown author')} on {catalog_metadata.get('date', 'an unknown date')}.
        Subject keywords associated with this catalog include: {catalog_metadata.get('subject', 'No subject keywords available')}.
        Description: {catalog_metadata.get('description', 'No additional description available')}.

        Your goal is to provide a comprehensive and accurate summary of the document's content with a focus on:
        - Key astronomy-related terms and themes mentioned.
        - Important dates, observations, and any references to instruments or methodologies used.
        - Notable insights or discoveries related to astronomy, as presented by the author or others.

        Ensure that the summary captures the core essence of the document, highlighting relevant terms, dates, instruments, and observations as fully as possible based on the context of this catalog.
        """

        # Define the user prompt
        prompt_content = '''
        Extract the following from this astronomy archive document:
        - Metadata (Author, Date, Title)
        - A summary of the document's content.
        - Astronomy-related terms mentioned in the document.
        '''

        # Define JSON schema for a structured output
        json_schema = {
            "name": "astronomy_archive_response",
            "schema": {
                "type": "object",
                "properties": {
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "author": {"type": "string"},
                            "date": {"type": "string"},
                            "title": {"type": "string"}
                        },
                        "required": ["author", "date", "title"],
                        "additionalProperties": False
                    },
                    "summary": {"type": "string"},
                    "astronomy_terms": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["metadata", "summary", "astronomy_terms"],
                "additionalProperties": False
            },
            "strict": True
        }
        print("before api call")           
        chat_output = openai_api.extract_info(model="gpt-4o", page=page, system_content=system_content, prompt_content=prompt_content, json_schema=json_schema )

        # Parse the JSON output from the API
        parsed_output = json.loads(chat_output)

        # Collect data for the final output
        extracted_data.append({
            'catalog_id': catalog_id,
            'page_num': page_num + 1,
            'metadata': parsed_output.get("metadata", {}),
            'summary': parsed_output.get("summary", ""),
            'astronomy_terms': parsed_output.get("astronomy_terms", [])
        })
    pdf.close()
    return extracted_data


def insert_into_rds(connection, json_list, catalog_meta):
    """Insert processed data into the RDS database."""
    inserted_catalogs = set()  # Track already inserted catalogs

    for item in json_list:
        json_list2 = {
            'page_num': item['page_num'],
            'catalog_id': item['catalog_id'],
            'metadata': item['metadata'],
            'summary': item['summary'],
            'astronomy_terms': item['astronomy_terms'],
        }
        print("Processing document:", json_list2)

        with connection.cursor() as cursor:
            catalog_id = json_list2["catalog_id"]

            # Insert catalog metadata if not already inserted
            if catalog_id not in inserted_catalogs:
                cursor.execute(
                    """
                    INSERT INTO Catalogs (catalog_id, title, subject, description, author, date, format, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        title = VALUES(title),
                        subject = VALUES(subject),
                        description = VALUES(description),
                        author = VALUES(author),
                        date = VALUES(date),
                        format = VALUES(format),
                        type = VALUES(type)
                    """,
                    (
                        catalog_id,
                        catalog_meta.get("title", ""),
                        catalog_meta.get("subject", ""),
                        catalog_meta.get("description", ""),
                        catalog_meta.get("creator", ""),
                        catalog_meta.get("date", ""),
                        catalog_meta.get("format", ""),
                        catalog_meta.get("type", ""),
                    )
                )
                inserted_catalogs.add(catalog_id)  # Add to set to avoid re-insertion

            # Insert document data
            terms_list_json = json.dumps(json_list2["astronomy_terms"])
            cursor.execute(
                """
                INSERT INTO Documents (page_num, catalog_id, author, title, date, summary, astronomy_terms)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    author = VALUES(author),
                    title = VALUES(title),
                    date = VALUES(date),
                    summary = VALUES(summary),
                    astronomy_terms = VALUES(astronomy_terms)
                """,
                (
                    json_list2["page_num"],
                    catalog_id,
                    json_list2["metadata"].get("author", ""),
                    json_list2["metadata"].get("title", ""),
                    json_list2["metadata"].get("date", ""),
                    json_list2["summary"],
                    terms_list_json,
                )
            )
            document_id = cursor.lastrowid  # Get the document ID for linking terms

            # Insert terms and build inverted index
            for term in json_list2["astronomy_terms"]:
                cursor.execute("INSERT IGNORE INTO Terms (term) VALUES (%s)", (term,))
                cursor.execute("SELECT term_id FROM Terms WHERE term = %s", (term,))
                term_id = cursor.fetchone()[0]

                # Link term to document
                cursor.execute(
                    "INSERT IGNORE INTO DocumentTerms (term_id, document_id) VALUES (%s, %s)",
                    (term_id, document_id),
                )

        connection.commit()
        print(f"Document '{json_list2['metadata']['title']}' inserted successfully!")


def lambda_handler(event, context):
    """Main Lambda handler function."""
    try:
        # Retrieve environment variables
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')
        openai_api_key = os.getenv('OPENAI_API_KEY')

        # Establish RDS connection
        connection = connect_to_rds()
        print(connection)

        # Parse S3 event
        # Uncomment for production
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Hardcoded for testing
        # bucket_name = "logbooks"  # Replace with actual bucket name
        # object_key = "1976.pdf.pdf"  # Replace with actual object key

        print(f"Downloading file from S3: Bucket={bucket_name}, Key={object_key}")
        
        # Download the PDF from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()

        # Debug file content
        if not file_content:
            raise ValueError("Downloaded file content is empty.")
        print(f"File content length: {len(file_content)}")

        # Retrieve metadata from S3 object
        catalog_metadata = response.get("Metadata", {})
        print(f"Retrieved Metadata: {catalog_metadata}")

        # Ensure metadata contains required fields
        if not catalog_metadata:
            print("Warning: No metadata found in the S3 object.")

        # Process the PDF and extract information
        print("Starting PDF processing...")
        processed_data = process_pdf(file_content, catalog_metadata)
        print(f"Processed Data: {processed_data}")

        # Insert processed data into the RDS database
        # Uncomment once ready to test database insertion
        # insert_into_rds(connection, object_key, processed_data)
        insert_into_rds(connection, processed_data, catalog_metadata)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data processed successfully.", "processed_data": processed_data})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": f"Processing failed: {e}"
        }


if __name__ == "__main__":
    # Example test event for local testing
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "logbooks"},
                    "object": {"key": "mars.pdf"}
                }
            }
        ]
    }
    context = None  # Context is only used in AWS Lambda, not needed for local testing

    # Call the lambda_handler function
    response = lambda_handler(event, context)

    # Print the response for debugging
    print(response)



    # ok yay it all wokred, now jsut fix prompt for the tabualted info for the 1976 logbook and store in rds 




    # now I can process more and load this into ec2 
    # to speed up theh project maybe   resinser the hson testing data into the db 
    # and then for the demo i do example uplaod and then show th eupdated metric/ dahsboard 
    # upaoda json iwth preporcessed docs in json 


