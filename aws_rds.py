import pymysql
import os
from dotenv import load_dotenv
load_dotenv()

# print(f"DB_HOST: {os.getenv('DB_HOST')}")
# print(f"DB_USER: {os.getenv('DB_USER')}")
# print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
# print(f"DB_NAME: {os.getenv('DB_NAME')}")
# print(f"DB_PORT: {os.getenv('DB_PORT')}")


def lambda_handler(event, context):
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT'))
        )
        print("Successfully connected to the database")

        # Example query
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW()")
            result = cursor.fetchone()
            print(f"Database time: {result}")

        # Close connection
        connection.close()
        return {
            "statusCode": 200,
            "body": "Database connection successful"
        }
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return {
            "statusCode": 500,
            "body": "Database connection failed"
        }


if __name__ == "__main__":
    event = {"test": "testConnection"}
    context = None  # Context is only used in AWS Lambda
    response = lambda_handler(event, context)
    print(response)
