import pytesseract 
import cv2  

# preprocessig
def pre_process_image(image_path):
    """pre-processes image """
    img = cv2.imread(image_path)
    
    if img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    img = cv2.resize(img, None, fx=0.3, fy=0.3)  
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)  
    return img


# processed_img = pre_process_image("documents/arithmetic.png")
processed_img = pre_process_image("OCR_testing/documents/tabular.tiff")

# ocr process:
text_extracted = pytesseract.image_to_string(processed_img)
print(text_extracted)

# for confidence score call image_to_data method
conf_df = pytesseract.image_to_data(processed_img, output_type='data.frame')
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

