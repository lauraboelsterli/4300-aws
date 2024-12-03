# extract all the formats given from meta 

# prompt for logbooks (arithemtic, if tabular return into json tabular format)

# come up with the n diff prompts 

# system prompt stays the same its just the actual text prompt thats changing now 

from chat_api import OpenAI 
from web_scrape import Scraper
import fitz  
import json
import os
import db_insert as sql
BASE_URL = "https://collectionslowellobservatory.omeka.net/items/browse"
ITEM_BASE_URL = "https://collectionslowellobservatory.omeka.net"
DOWNLOAD_FOLDER = "lowell_downloads"
SCRAPEME_LIST = ['subject', 'description', 'creator', 'date', 'format', 'language', 'type', 'identifier']
# CACHE_FILE = "catalog_metadata.json"
CACHE_FILE = "metadata.json"

#----------------------------------------------------------------------------------------------------------------------
# could do: if catalog has mutliple fomrats then just concat the prompt for all the diff categories and tell chat
# if the given doc, then extract this, if its calculations then, if its wirrintg then (doc per doc decision making prompting)
# and still have the core metdata like astro terms (maybe i should prompt it to count the number of times the astro keyword 
# is used in that doc) and summaries and historical context (optional)
# to be extracted for every doc regardless of the type 
#----------------------------------------------------------------------------------------------------------------------

def unique_catalogs(CACHE_FILE):
    '''takes in all of the diff catalog types extracted and then gives back set of all types
    returns all unique catalog types'''
    with open(CACHE_FILE, 'r') as file:
        data = json.load(file)
    # get all the formats from the catalogs 
    formats = []
    for item in data:
        formats.append(data[item]['Format'])
    u_format = list(set(formats))
    return u_format

# output w curent metadata file: 
# ['Handwritten letter', 'Handwritten document', 'Observation notes', 'Typed document', 'Calculations', 'Published paper']
# based on the diff catalogs, there seems to be writing, observation notes, calclations, photographs ----------
#                                                                                                   where is the doc 
#                                                                                                   of all the info i wanted 
#                                                                                                   to extract?
#                                                                                                   (if not on a doc, 
#                                                                                                   then its in my openai chat history)
# the prompts:
# for_all_types = (the same schema as rn) but also ask astro term frequency, historical references/historical context (if any), other collaborators (if any), astronomy context (if any)
    # logbook/calculations =  for_all_types + "if possible return in json tabular format to mimic the image given, if not tabular extract all arithmetic 
    # and relevant info to the document based on the context of the catalog (system), focus on plate id, RA, declination, exposure time, seeing, instruments, etc."
    # text = for_all_types + "tone, maybe even ask for a full transcirption for these docs"
    # photographs = for_all_types + "plate id and description of the image"


# the next steps (3 steps):
# 1. implement new prompt conditionals in main then give prompt to the api
# 2. have to also change the json schema for each given scenario 
# 3. then chnage db schema 


# Step 1:
# new prompting implementation:
# system prompt (edited): "fix the bottom part of the prompt, its redundant"

# new json schemas:
# json schema for logbooks/calculations: - get list of all plate ids and then also, if tabular give back the 
# whole table in tabular json, if not tabular must have plateid and extract the same info
#         # Define JSON schema for a structured output
#         json_schema = {
#             "name": "astronomy_archive_response",
#             "schema": {
#                 "type": "object",
#                 "properties": {
#                     "metadata": {
#                         "type": "object",
#                         "properties": {
#                             "author": {"type": "string"},
#                             "date": {"type": "string"},
# can i make the date convert it to a consistent date fomrat (helps me with post-processing)???
#                             "title": {"type": "string"}, 
#                              "collaborators": {"type": "array",
#                         "items": {"type": "string"}},
#                         "required": ["author", "date", "title"],
#                         "additionalProperties": False
#                     },
#                     "summary": {"type": "string"},
#                      "historical_context": {"type": "string"},
#                      "astronomy_context": {"type": "string"},
#                     "astronomy_terms": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     }
#                 },
# how do i implement the astronomy terms to be a dct with word as key mapped to term freq in that doc???
#                 "required": ["metadata", "summary", "astronomy_terms"],
#                 "additionalProperties": False
#             },
#             "strict": True
#         }


# json schema for text:
#         # Define JSON schema for a structured output
#         json_schema = {
#             "name": "astronomy_archive_response",
#             "schema": {
#                 "type": "object",
#                 "properties": {
#                     "metadata": {
#                         "type": "object",
#                         "properties": {
#                             "author": {"type": "string"},
#                             "date": {"type": "string"},
# can i make the date convert it to a consistent date fomrat (helps me with post-processing)???
#                             "title": {"type": "string"}, 
#                              "collaborators": {"type": "array",
#                         "items": {"type": "string"}},
#                         "required": ["author", "date", "title"],
#                         "additionalProperties": False
#                     },
#                     "summary": {"type": "string"},
#                      "historical_context": {"type": "string"},
#                      "astronomy_context": {"type": "string"},
#                     "astronomy_terms": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     }
#                 },
# how do i implement the astronomy terms to be a dct with word as key mapped to term freq in that doc???
#                 "required": ["metadata", "summary", "astronomy_terms"],
# for the text docs i could make the hisorical context/astro context required.....
#                 "additionalProperties": False
#             },
#             "strict": True
#         }


# json schema for images:
#         # Define JSON schema for a structured output
#         json_schema = {
#             "name": "astronomy_archive_response",
#             "schema": {
#                 "type": "object",
#                 "properties": {
#                     "metadata": {
#                         "type": "object",
#                         "properties": {
#                             "author": {"type": "string"},
#                             "date": {"type": "string"},
# can i make the date convert it to a consistent date fomrat (helps me with post-processing)???
#                             "title": {"type": "string"}, 
#                              "collaborators": {"type": "array",
#                         "items": {"type": "string"}},
#                         "required": ["author", "date", "title"],
#                         "additionalProperties": False
#                     },
#                       "image_description": {"type": "string"},
#                       "plate_id": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     },
#                     "summary": {"type": "string"},
#                      "historical_context": {"type": "string"},
#                      "astronomy_context": {"type": "string"},
#                     "astronomy_terms": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     }
#                 },
# how do i implement the astronomy terms to be a dct with word as key mapped to term freq in that doc???
#                 "required": ["metadata", "summary", "astronomy_terms"],
#                 "additionalProperties": False
#             },
#             "strict": True
#         }









def main():
    # BASE_URL = "https://collectionslowellobservatory.omeka.net/items/browse"
    # ITEM_BASE_URL = "https://collectionslowellobservatory.omeka.net"
    # DOWNLOAD_FOLDER = "lowell_downloads"
    # SCRAPEME_LIST = ['subject', 'description', 'creator', 'date', 'format', 'language', 'type', 'identifier']
    # # CACHE_FILE = "catalog_metadata.json"
    # CACHE_FILE = "metadata.json"
    openai_api = OpenAI()
    scraper = Scraper(BASE_URL, ITEM_BASE_URL, DOWNLOAD_FOLDER, SCRAPEME_LIST)

    # Scrape and download metadata and files
    # max_items_to_download = 10  # testing limit for donwload and webscraping 
    # scraper.scrape_and_download(max_items=max_items_to_download, cache_file=CACHE_FILE)

    print(unique_catalogs(CACHE_FILE))



    # Folder containing PDFs to process
    # folder_path = DOWNLOAD_FOLDER
    # catalog_limit = 0  # Limit to api processing 
    # page_limit = 0 # Limit to api processing 
    # final_doc_output = []
    # total_catalogs_processed = 0

    # for filename in os.listdir(folder_path):
    #     if total_catalogs_processed >= catalog_limit:
    #         print("Reached catalog processing limit. Stopping.")
    #         break

    #     if filename.endswith('.pdf'):
    #         catalog_id = os.path.splitext(filename)[0]  
    #         file_path = os.path.join(folder_path, filename)
    #         # Retrieve metadata for this catalog
    #         catalog_metadata = scraper.get_metadata_by_id(catalog_id)
    #         # print(f"Metadata for catalog {catalog_id}: {catalog_metadata}")
    #         if catalog_metadata:
    #             print(f"Processing metadata for catalog {catalog_id}: {catalog_metadata}")
    #             total_catalogs_processed += 1
    #         else:
    #             print(f"No metadata found for catalog {catalog_id}.")

    #         # get tailored system content for every catalog
    #         system_content = f"""
    #         You are a helpful assistant analyzing and extracting information from historical astronomy documents.
    #         This document is part of a catalog titled "{catalog_metadata.get('Title', 'Unknown Title')}" and is a 
    #         {catalog_metadata.get('Format', 'Unknown Format')} of {catalog_metadata.get('Type', 'Unknown Type')} in {catalog_metadata.get('Language', 'Unknown Language')},
    #         created by {catalog_metadata.get('Creator', 'an unknown author')} on {catalog_metadata.get('Date', 'an unknown date')}.
    #         Subject keywords associated with this catalog include: {catalog_metadata.get('Subject', 'No subject keywords available')}.
    #         Description: {catalog_metadata.get('Description', 'No additional description available')}.

    #         Your goal is to provide a comprehensive and accurate summary of the document's content with a focus on:
    #         - Key astronomy-related terms and themes mentioned.
    #         - Important dates, observations, and any references to instruments or methodologies used.
    #         - Notable insights or discoveries related to astronomy, as presented by the author or others.

    #         Ensure that the summary captures the core essence of the document, highlighting relevant terms, dates, instruments, and observations as fully as possible based on the context of this catalog.
    #         """

    #         # Define the user prompt
    #         prompt_content = '''
    #         Extract the following from this astronomy archive document:
    #         - Metadata (Author, Date, Title)
    #         - A summary of the document's content.
    #         - Astronomy-related terms mentioned in the document.
    #         '''

    #         # Define JSON schema for a structured output
    #         json_schema = {
    #             "name": "astronomy_archive_response",
    #             "schema": {
    #                 "type": "object",
    #                 "properties": {
    #                     "metadata": {
    #                         "type": "object",
    #                         "properties": {
    #                             "author": {"type": "string"},
    #                             "date": {"type": "string"},
    #                             "title": {"type": "string"}
    #                         },
    #                         "required": ["author", "date", "title"],
    #                         "additionalProperties": False
    #                     },
    #                     "summary": {"type": "string"},
    #                     "astronomy_terms": {
    #                         "type": "array",
    #                         "items": {"type": "string"}
    #                     }
    #                 },
    #                 "required": ["metadata", "summary", "astronomy_terms"],
    #                 "additionalProperties": False
    #             },
    #             "strict": True
    #         }
    
    #         pdf = fitz.open(file_path)
    #         # total_catalogs_processed += 1
    #         print(f"Processing catalog: {catalog_id}")

    #         pages_processed = 0
    #         for page_num in range(pdf.page_count):
    #             if pages_processed >= page_limit:
    #                 print("Reached page processing limit. Stopping.")
    #                 break
    #             pages_processed +=1
    #             try:
    #                 # Get the page
    #                 page = pdf[page_num]
                    
    #                 chat_output = openai_api.extract_info(model="gpt-4o", page=page, system_content=system_content, prompt_content=prompt_content, json_schema=json_schema )

    #                 # Parse the JSON output from the API
    #                 parsed_output = json.loads(chat_output)

    #                 # Collect data for the final output
    #                 final_doc_output.append({
    #                     'catalog_id': catalog_id,
    #                     'page_num': page_num + 1,
    #                     'metadata': parsed_output.get("metadata", {}),
    #                     'summary': parsed_output.get("summary", ""),
    #                     'astronomy_terms': parsed_output.get("astronomy_terms", [])
    #                 })
    #             except Exception as e:
    #                 print(f"Error processing page {page_num + 1} in file {filename}: {e}")
    #                 continue

    #         pdf.close()

    # # print(final_doc_output)
    # print(f"Processing complete. {len(final_doc_output)} pages processed.")


    '''
    note: 
    if you want to run the api and insert the data into the database, then uncomment the block of code below.
    if you want to run the dashboard with the preloaded testing data then go to dash.py and run that instead
    '''
    # output JSON file path
    # mock_file_path = "testing_output.json"

    # # write final_doc_output form openai output to JSON file
    # try:
    #     with open(mock_file_path, 'w', encoding='utf-8') as json_file:
    #         json.dump(final_doc_output, json_file, indent=4, ensure_ascii=False)
    #     print(f"Data successfully written to {mock_file_path}")
    # except Exception as e:
    #     print(f"Error writing to JSON file: {e}")


    # with open(mock_file_path, "r", encoding="utf-8") as file:
    #     mock_data = json.load(file)


    # db_path = "starchive2.db"
    # mock_file_path = "two_cat_testing.json"

    # with open(mock_file_path, "r") as file:
    #     mock_data = json.load(file)

    # # sql.clear_db()

    # for record in mock_data:
    #     # Extract necessary fields for insertion
    #     processed_docs = {
    #         'page_num': record['page_num'],
    #         'catalog_id': record['catalog_id'],
    #         'metadata': record['metadata'],
    #         'summary': record['summary'],
    #         'astronomy_terms': record['astronomy_terms']
    #     }

    #     # Extract catalog identifier (directly from record['catalog_id'])
    #     identifier = record['catalog_id']

    #     # Retrieve catalog metadata using the identifier
    #     catalog_meta = scraper.get_metadata_by_id(identifier)
    #     # print(catalog_meta)

        
    #     # Insert into db
    #     sql.insert_document(db_path, processed_docs, catalog_meta)



main()