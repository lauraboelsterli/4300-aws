'''
tabulated updated api call prompt production file 
'''
'''first ever test fot tabulated extraction
Processed Data: [{'catalog_id': '1976.pdf', 'page_num': 4, 'tabular_data': [{'plate_id': '5291', 'right_ascension': '8h 4m', 'declination': "+21° 32'", 'exposure_time': '7:51 – 8:13; 8:14 – 8:36', 'seeing_conditions': 'Good', 'instrument_used': '8x10 103aO', 'astronomer': '', 'notes': ''}, {'plate_id': '5294', 'right_ascension': '5h 45m', 'declination': "-50° 3'", 'exposure_time': '8:58 – 9:20; 9:21 – 9:43', 'seeing_conditions': 'Good', 'instrument_used': '5 Oak 8x10 103aO', 'astronomer': '', 'notes': ''}, {'plate_id': '5296', 'right_ascension': '11h', 'declination': "+45° 2'", 'exposure_time': '9:58 – 10:20', 'seeing_conditions': 'Good', 'instrument_used': 'HIS 103aO', 'astronomer': '', 'notes': 'R. Millis'}, {'plate_id': '5297', 'right_ascension': '0h 47m 35.3s', 'declination': '-48° 06\' 19"', 'exposure_time': '10:21 – 10:43', 'seeing_conditions': 'Good', 'instrument_used': 'HIS 103aO', 'astronomer': 'H. L. Giclas', 'notes': ''}, {'plate_id': '5312', 'right_ascension': '1h 18m', 'declination': "+43° 35'", 'exposure_time': '11:00 – 11:22', 'seeing_conditions': 'Good', 'instrument_used': 'HIS 103aO', 'astronomer': 'BAS', 'notes': ''}, {'plate_id': '5313', 'right_ascension': '0h 29m', 'declination': "+43° 35'", 'exposure_time': '11:23 – 11:45', 'seeing_conditions': 'Good', 'instrument_used': 'HIS 103aO', 'astronomer': 'MW', 'notes': 'SA 57'}, {'plate_id': '5319', 'right_ascension': '12h 26m 27s', 'declination': "+29° 48'", 'exposure_time': '12:00 – 12:22', 'seeing_conditions': 'Good', 'instrument_used': '8x10 103aO', 'astronomer': '', 'notes': 'No E Foid'}], 'extra_information': '', 'metadata': {'author': 'Giclas, Henry; Burnham, Robert; Thomas, Norman; Millis, Bob; Bowell, Ted; ELGB; BAS; MW', 'date': '1976-04-27', 'title': '13-inch Observation Logbook, 1976'}}]
{'statusCode': 200, 'body': '{"message": "Data processed successfully.", "processed_data": [{"catalog_id": "1976.pdf", "page_num": 4, "tabular_data": [{"plate_id": "5291", "right_ascension": "8h 4m", "declination": "+21\\u00b0 32\'", "exposure_time": "7:51 \\u2013 8:13; 8:14 \\u2013 8:36", "seeing_conditions": "Good", "instrument_used": "8x10 103aO", "astronomer": "", "notes": ""}, {"plate_id": "5294", "right_ascension": "5h 45m", "declination": "-50\\u00b0 3\'", "exposure_time": "8:58 \\u2013 9:20; 9:21 \\u2013 9:43", "seeing_conditions": "Good", "instrument_used": "5 Oak 8x10 103aO", "astronomer": "", "notes": ""}, {"plate_id": "5296", "right_ascension": "11h", "declination": "+45\\u00b0 2\'", "exposure_time": "9:58 \\u2013 10:20", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "", "notes": "R. Millis"}, {"plate_id": "5297", "right_ascension": "0h 47m 35.3s", "declination": "-48\\u00b0 06\' 19\\"", "exposure_time": "10:21 \\u2013 10:43", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "H. L. Giclas", "notes": ""}, {"plate_id": "5312", "right_ascension": "1h 18m", "declination": "+43\\u00b0 35\'", "exposure_time": "11:00 \\u2013 11:22", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "BAS", "notes": ""}, {"plate_id": "5313", "right_ascension": "0h 29m", "declination": "+43\\u00b0 35\'", "exposure_time": "11:23 \\u2013 11:45", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "MW", "notes": "SA 57"}, {"plate_id": "5319", "right_ascension": "12h 26m 27s", "declination": "+29\\u00b0 48\'", "exposure_time": "12:00 \\u2013 12:22", "seeing_conditions": "Good", "instrument_used": "8x10 103aO", "astronomer": "", "notes": "No E Foid"}], "extra_information": "", "metadata": {"author": "Giclas, Henry; Burnham, Robert; Thomas, Norman; Millis, Bob; Bowell, Ted; ELGB; BAS; MW", "date": "1976-04-27", "title": "13-inch Observation Logbook, 1976"}}]}'}
'''
import boto3
import pymysql
import requests
import os
import json
from chat_api import OpenAI 
import fitz  
import pandas as pd 


# Initialize AWS clients
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

def process_pdf(file_content, catalog_metadata, limit=1):
    """Extract text from a PDF and call the OpenAI API."""
    pdf = fitz.open(stream=file_content, filetype="pdf")
    extracted_data = []
    catalog_id = catalog_metadata.get('identifier', 'Unknown identifier')
    start_page = 3 
    for page_num in range(start_page, pdf.page_count):
        if page_num - start_page >= limit:
            break 
        page = pdf[page_num]

        system_content = f"""
        You are a helpful assistant analyzing and extracting information from historical astronomy observation logbooks.
        This document is part of a catalog titled "{catalog_metadata.get('title', 'Unknown Title')}" and is a 
        {catalog_metadata.get('format', 'Unknown Format')} of {catalog_metadata.get('type', 'Unknown Type')} in {catalog_metadata.get('language', 'Unknown Language')},
        created by {catalog_metadata.get('creator', 'an unknown author')} on {catalog_metadata.get('date', 'an unknown date')}.
        Subject keywords associated with this catalog include: {catalog_metadata.get('subject', 'No subject keywords available')}.
        Description: {catalog_metadata.get('description', 'No additional description available')}.

        Your goal is to provide accurate extraction of all the information in these tables and from the overall document.
        Focus on:
        - Key astronomy-related terms and themes mentioned.
        - Important dates, observations, and any references to instruments or methodologies used.
        - Notable insights or discoveries related to astronomy, as presented by the author or others.

        Return the information in a JSON tabular format, and if there's any additional information or information on the document 
        that deviates from a tabulated structure, include that as extra JSON output.
        """

        prompt_content = '''
        Extract the observation log archive content into a tabular format, and the most important rows to retrieve consistently are:
        - Plate IDs
        - Right Ascension 
        - Declination
        - Exposure Time
        - Seeing Conditions
        - Instrument used 
        - Astronomer 
        - Any additional notes 
        '''
        # prompt_content = '''extract the exact table into json tabular format '''
        json_schema = {
            "name": "astronomy_observation_log_response",
            "schema": {
                "type": "object",
                "properties": {
                    "tabular_data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "plate_id": {"type": "string"},
                                "right_ascension": {"type": "string"},
                                "declination": {"type": "string"},
                                "exposure_time": {"type": "string"},
                                "seeing_conditions": {"type": "string"},
                                "instrument_used": {"type": "string"},
                                "astronomer": {"type": "string"},
                                "notes": {"type": "string"}
                            },
                            "required": [
                                "plate_id",
                                "right_ascension",
                                "declination",
                                "exposure_time",
                                "seeing_conditions",
                                "instrument_used",
                                "astronomer",
                                "notes"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "extra_information": {
                        "type": "string"
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "author": {"type": "string"},
                            "date": {"type": "string"},
                            "title": {"type": "string"}
                        },
                        "required": ["author", "date", "title"],
                        "additionalProperties": False
                    }
                },
                # Add all top-level keys to the `required` array
                "required": ["tabular_data", "extra_information", "metadata"],
                "additionalProperties": False
            },
            "strict": True
        }




        chat_output = openai_api.extract_info(
            model="gpt-4o",
            page=page,
            system_content=system_content,
            prompt_content=prompt_content,
            json_schema=json_schema)

        parsed_output = json.loads(chat_output)

        extracted_data.append({
            'catalog_id': catalog_id,
            'page_num': page_num + 1,
            # 'chatoutput': parsed_output
            'tabular_data': parsed_output.get("tabular_data", []),
            'extra_information': parsed_output.get("extra_information", ""),
            'metadata': parsed_output.get("metadata", {})
        })

    pdf.close()
    return extracted_data

# def insert_into_rds(connection, catalog_id, page_data):
#     """Insert processed data into the RDS database."""
#     with connection.cursor() as cursor:
#         for record in page_data:
#             query = """
#             INSERT INTO processed_documents (catalog_id, page_num, extracted_text, api_response)
#             VALUES (%s, %s, %s, %s)
#             """
#             cursor.execute(query, (
#                 catalog_id,
#                 record['page_num'],
#                 record['extracted_text'],
#                 json.dumps(record['api_response'])
#             ))
#         connection.commit()


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

        # Parse S3 event
        # Uncomment for production
        # record = event['Records'][0]
        # bucket_name = record['s3']['bucket']['name']
        # object_key = record['s3']['object']['key']

        # Hardcoded for testing
        bucket_name = "logbooks"  # Replace with actual bucket name
        object_key = "1976.pdf.pdf"  # Replace with actual object key

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
                    "object": {"key": "1976.pdf.pdf"}
                }
            }
        ]
    }
    context = None  # Context is only used in AWS Lambda, not needed for local testing

    # Call the lambda_handler function
    response = lambda_handler(event, context)

    # Print the response for debugging
    print(response)


    rows = []
    for entry in response:
        catalog_id = entry["catalog_id"]
        page_num = entry["page_num"]
        metadata = entry["metadata"]
        
        for record in entry["tabular_data"]:
            row = {
                "catalog_id": catalog_id,
                "page_num": page_num,
                "author": metadata.get("author", ""),
                "date": metadata.get("date", ""),
                "title": metadata.get("title", ""),
                **record
            }
            rows.append(row)

    df = pd.DataFrame(rows)

    # Display the DataFrame
    print(df)




