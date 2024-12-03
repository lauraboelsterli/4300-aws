import requests
from bs4 import BeautifulSoup
import time
import os
from itertools import count
from urllib.parse import urlparse, parse_qs
import json


class MetadataRetrieval:

    def __init__(self, base_url, item_url):
        self.base_url = base_url
        self.item_url = item_url

    def get_page_soup(self, url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def extract_lowell_metadata(self, scrapeme_list, item_url):
        soup = self.get_page_soup(item_url)
        metadata = {}
        title_element = soup.find('h1')
        # remove unnecessary quotes (for json loads)
        if title_element:
            title_cleaned = title_element.text.strip('"')
            metadata['Title'] = title_cleaned
        else:
            metadata['Title'] = "Not available"

        for topic in scrapeme_list:
            field_element = soup.find('div', id=f'dublin-core-{topic}')
            if field_element:
                value_element = field_element.find('div', class_='element-text')



                #-------------------------------------------------------------------------------------------------
                # have to edit this as sometimes when for for example creator there are multiple and are sepreated by<br> and 
                # i would need to fix that so i can retireve all authors 

                # i think only the observation logs ar efomratted with br and the other ones are just multiple divs - was correct soo maybe i identify based on the metdata 
                # and then have a seperate emthod for extarcting all the info for log books, but for the tradiitonal route i just need to deal with multiple 
                # dvis when multiple entires exist 
                # if value_element == "Observation notes": or use is in as there might be multiple? 
                #     # then i wan to implement the logbook logic for extracting all chars 
                # else ( if its yathing else):
                # implement the logic of being able to retrive multiple things not jsu the first item with the div logic 
                #---------------------------------------------------------------------------------------------------



                raw_text = value_element.text.strip() if value_element else "Not available"
                metadata[topic.capitalize()] = raw_text
            else:
                metadata[topic.capitalize()] = "Not available"

        # Extract PDF viewer URL from iframe and get the direct PDF link
        iframe = soup.find('iframe', src=True)
        if iframe:
            viewer_url = iframe['src']
            parsed_url = urlparse(viewer_url)
            direct_pdf_url = parse_qs(parsed_url.query).get('file', [None])[0]  # Extract the 'file' param
            metadata['pdf_url'] = direct_pdf_url

        # Process all metadata fields at the end
        metadata = json.loads(json.dumps(metadata))
 
        return metadata

    def scrape_items(self, scrapeme_list, max_items=None):
        all_metadata = {}
        item_counter = 0
        for page_num in range(1, 162):
            page_url = f"{self.base_url}?page={page_num}"
            soup = self.get_page_soup(page_url)
            items = soup.find_all('div', class_="single-line item record")
            for item in items:
                if max_items and item_counter >= max_items:
                    print("Reached scraping limit.")
                    return all_metadata
                title_tag = item.find('h4')
                item_link = title_tag.find('a', href=True)['href'] if title_tag else None
                item_url = f"{self.item_url}{item_link}" if item_link else None
                if item_url:
                    metadata = self.extract_lowell_metadata(scrapeme_list, item_url)
                    identifier = metadata.get("Identifier", "unknown")
                    all_metadata[identifier] = metadata
                    item_counter += 1
        return all_metadata




class Download:
    def __init__(self, folder):
        self.folder = folder

    def ensure_folder_exists(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def download_pdf(self, pdf_url, identifier="document"):
        self.ensure_folder_exists()
        pdf_path = os.path.join(self.folder, f"{identifier}.pdf")
        if os.path.exists(pdf_path):
            print(f"PDF already exists: {pdf_path}, skipping download.")
            return pdf_path
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(pdf_path, 'wb') as file:
                file.write(response.content)
            print(f"PDF saved: {pdf_path}")
            return pdf_path
        else:
            print(f"Failed to download PDF: {pdf_url}")
            return None
        

class Scraper:
    def __init__(self, base_url, item_base_url, download_folder, scrapeme_list):
        self.metadata_getter = MetadataRetrieval(base_url, item_base_url)
        self.downloader = Download(download_folder)
        self.scrapeme_list = scrapeme_list
        self.catalog_metadata = {}  # metadata stored for each catalog by identifier

    def save_metadata_to_file(self, filename="metadata.json"):
        with open(filename, "w") as f:
            json.dump(self.catalog_metadata, f, indent=4)
        print(f"Metadata saved to {filename}.")

    def load_metadata_from_file(self, filename="metadata.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.catalog_metadata = json.load(f)
            print(f"Metadata loaded from {filename}.")
            return True
        else:
            print(f"{filename} does not exist. Metadata not loaded.")
            return False
        
    def load_metadata(self, max_items=None, cache_file="metadata.json"):
        if not self.load_metadata_from_file(cache_file):
            print("Scraping metadata from the web...")
            self.catalog_metadata = self.metadata_getter.scrape_items(self.scrapeme_list, max_items)
            print(f"Loaded metadata for {len(self.catalog_metadata)} items.")
            self.save_metadata_to_file(cache_file)

    def get_metadata_by_id(self, catalog_id):
        return self.catalog_metadata.get(catalog_id, None)
    

    # re scrape_and_download method
    # ----------------------------------------------------------------------------------------------------------------------- 
    # idk why its not donwloading the missing files when i up the max download param, the extracting metadata works
    # perfect jst not donwloading the missing files of files i already scraped metadata for 
    # its to ensure that you can put max items to any level and have the necessary file with your desired max downloads 
    # -----------------------------------------------------------------------------------------------------------------------   
    # maybe i jut donwload all metadata seprately upload it to json and then do the scraping for metadata seperately



    def scrape_and_download(self, max_items=None, cache_file="metadata.json"):
        # Attempt to load metadata from cache
        if not self.load_metadata_from_file(cache_file):
            # if not the length of max items then jusut renew the catalog meta json 
            print("Scraping metadata from the web...")
            all_metadata = self.metadata_getter.scrape_items(self.scrapeme_list, max_items=max_items)
            self.catalog_metadata = all_metadata
            self.save_metadata_to_file(cache_file)  # Save the scraped metadata for future use
        else:
            print("Loaded metadata from cache.")

        # Download missing PDFs
        catalogs_processed = 0
        for identifier, metadata in self.catalog_metadata.items():
            pdf_path = os.path.join(self.downloader.folder, f"{identifier}.pdf")

            # Check if the file exists
            if not os.path.exists(pdf_path):
                pdf_url = metadata.get('pdf_url')
                if pdf_url:
                    print(f"Downloading file for identifier: {identifier}")
                    self.downloader.download_pdf(pdf_url, identifier)
                    # downloaded_count += 1
                else:
                    print(f"No PDF URL found for identifier: {identifier}")
            else:
                print(f"File already exists for identifier: {identifier}, skipping download.")

            catalogs_processed += 1
            # Stop if the max download limit is reached
            if max_items and catalogs_processed >= max_items:
                print(f"Reached maximum catalogs download and scraping limit of {max_items}.")
                break

        print(f"Scraped, downloaded, and stored {catalogs_processed} files.")
        return self.catalog_metadata




# testing:

# def main():
#     BASE_URL = "https://collectionslowellobservatory.omeka.net/items/browse"
#     ITEM_BASE_URL = "https://collectionslowellobservatory.omeka.net"
#     DOWNLOAD_FOLDER = "lowell_downloads"
#     SCRAPEME_LIST = ['subject', 'description', 'creator', 'date', 'format', 'language', 'type', 'identifier']

#     scraper = Scraper(BASE_URL, ITEM_BASE_URL, DOWNLOAD_FOLDER, SCRAPEME_LIST)
#     metadata = scraper.scrape_and_download(max_items_to_download=2)
#     print(metadata)


# main()

# def main():
#     # Constants
#     BASE_URL = "https://collectionslowellobservatory.omeka.net/items/browse"
#     ITEM_BASE_URL = "https://collectionslowellobservatory.omeka.net"
#     DOWNLOAD_FOLDER = "lowell_downloads"
#     SCRAPEME_LIST = ['subject', 'description', 'creator', 'date', 'format', 'language', 'type', 'identifier']
#     # Initialize Scraper
#     scraper = Scraper(BASE_URL, ITEM_BASE_URL, DOWNLOAD_FOLDER, SCRAPEME_LIST)
#     # Build catalog metadata
#     catalog_id = "PL_PMSS_B5_F10"
#     scraper.load_metadata(max_items=30)  
#     # stored = scraper.get_metadata_by_id(catalog_id)
#     scraper.scrape_and_download(max_items=30)
#     # print(stored)

#     # has to take in multiple subjects 
#     # mulstiple creators, dates, formats, and type

# main()
