# stuff that used to be in the code 
# model="chatgpt-4o-latest"
# "text": "extract all dates and astronomical search terms from this document"

import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("set the OPENAI_API_KEY in a .env file")

client = OpenAI(api_key=api_key)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

image_path = "OCR_testing/documents/text_arithmetic.png"

base64_image = encode_image(image_path)

# this is old api call:

response = client.chat.completions.create(
  model="chatgpt-4o-latest",
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "extract all dates and astronomical search terms from this document",
        },
        {
          "type": "image_url",
          "image_url": {
            "url":  f"data:image/png;base64,{base64_image}"
          },
        },
      ],
    }
  ],
)

print(response.choices[0])
# print(response.to_json)

# this is new api call method:

# # attempting with predefined schema 
# json_schema = {
#     "name": "astronomy_archive_response",
#     "schema": {
#         "type": "object",
#         "properties": {
#             "metadata": {
#                 "type": "object",
#                 "properties": {
#                     "author": {"type": "string"},
#                     "date": {"type": "string"},
#                     "title": {"type": "string"}
#                 },
#                 "required": ["author", "date", "title"],
#                 "additionalProperties": False
#             },
#             "summary": {"type": "string"},
#             "astronomy_terms": {
#                 "type": "array",
#                 "items": {"type": "string"}
#             }
#         },
#         "required": ["metadata", "summary", "astronomy_terms"],
#         "additionalProperties": False
#     },
#     "strict": True
# }

# # experimenting with system settings 
# # Example metadata with description
# metadata = {
#     "title": "Pluto Plate Envelope",
#     "document_type": "Handwritten document",
#     "format": "Handwritten document",
#     "author": "Clyde Tombaugh",
#     "date": "1930-02-18",
#     "subject": "Pluto; Planet X; Astronomy; Planetary Discovery; Lowell Observatory; Tombaugh, Clyde; Flagstaff, Arizona.",
#     "description": "This envelope held the original plates with the official discovery images of Pluto. Percival Lowell first began the search in 1905, but died just fourteen years before the discovery was made on February 18, 1930. The cover contains notes on the discovery recorded by Clyde Tombaugh, including the telescope used, the search process, and other astronomical objects included on the plate image. The very bottom of the envelope features an excited note inscribed by Clyde Tombaugh that reads, 'Planet 'X' (Pluto) at last found!!!'"
# }

# # Update system content with the full metadata context
# system_content = f"""
# You are a helpful assistant analyzing historical astronomy documents.
# This document is titled "{metadata['title']}" and is a {metadata['format']} created by {metadata.get('author', 'unknown author')} on {metadata.get('date', 'unknown date')}.
# Subject keywords include: {metadata.get('subject', 'No subject keywords available')}.
# Description: {metadata.get('description', 'No additional description available')}.
# Focus on extracting specific astronomy-related terms, important dates, references to astronomical instruments, and any notable observations or inscriptions, especially in the context of the discovery of Pluto.
# """




# # # Prepare the prompt
# prompt_content = '''
#     Extract the following from this astronomy archive document:
#     - Metadata (Author, Date, Title)
#     - A summary of the document's content.
#     - Astronomy-related terms mentioned in the document.
# '''

# # Make the API call with response_format using json_schema
# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[{"role": "system", "content": system_content},
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": prompt_content,
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/png;base64,{base64_image}"
#                     }
#                 }
#             ]
#         }
#     ],
#     response_format={
#         "type": "json_schema",
#         "json_schema": json_schema
#     }
# )

# # Print the parsed response
# print(response.choices[0].message.content)