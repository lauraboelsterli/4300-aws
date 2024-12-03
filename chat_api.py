import openai
import dotenv
import os
import base64
import io

# all are prompted for the current metadata extracted from json schema + historical references (this extracted info is optional tho and can
# be null)
# then the deviations from there will depend on format type of the catalog (at least three diff ones)
# maybe i should scrape all metadata wihtout donwlading ans store that to see the unique formats there are 

class OpenAI:
    def __init__(self):
        dotenv.load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("Please set the OPENAI_API_KEY in a .env file")
        self.client = openai.OpenAI(api_key=api_key)

    @staticmethod
    def encode_image(page):
        '''converts a Pixmap to a Base64-encoded JPEG string ( necessary processing for Pdfs )'''
        pixmap = page.get_pixmap()
        image_bytes = pixmap.tobytes("jpeg")
        image_buffer = io.BytesIO(image_bytes)
        return base64.b64encode(image_buffer.read()).decode('utf-8')
        

    def extract_info(self, system_content, prompt_content, json_schema, page=None, model="gpt-4o"):
        '''Extracts information from a document, including metadata, summary, and astronomy terms'''
        base64_image = self.encode_image(page)

        # Make the API call
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_content,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            }
        )

        return response.choices[0].message.content




