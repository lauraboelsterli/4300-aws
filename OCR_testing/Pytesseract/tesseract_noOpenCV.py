import pytesseract 
from PIL import Image

# image_path = "documents/arithmetic.png"
image_path = "OCR_testing/documents/tabular.tiff"
img = Image.open(image_path)
    
# ocr process:
text_extracted = pytesseract.image_to_string(img)
print(text_extracted)

# for confidence score call image_to_data method
conf_df = pytesseract.image_to_data(img, output_type='data.frame')
# drop all non-test entries (aka all entires that do not have a confidence score)
only_conf_df = conf_df[conf_df.conf != -1].copy()
# print(only_conf_df["conf"].mean()) # oops i didnt normalize this 

# Normalize the confidence column
min_conf = only_conf_df['conf'].min()
max_conf = only_conf_df['conf'].max()

only_conf_df['normalized_conf'] = (only_conf_df['conf'] - min_conf) / (max_conf - min_conf)
# print(only_conf_df)
# confidence score on averge of all the words extracted 
print("Average Confidence Score:", only_conf_df["normalized_conf"].mean())

