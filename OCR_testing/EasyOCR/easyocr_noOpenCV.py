'''
note to me: to-do: add text ocr output into pandas df if tabular image to make output easier to read
-- stay posted 
'''
import cv2
import easyocr
import pandas as pd

# READ IMAGE
img = cv2.imread('OCR_testing/documents/tabular.tiff')
# img = cv2.imread('documents/structured_text.png')
    
reader = easyocr.Reader(['en'])
extracted_text = reader.readtext(img)
print("Extracted Text from Table:", extracted_text)

# List to store confidence scores (averaging all word confidence scores in the image)
confidence_scores = []
for t in extracted_text:
    # Each result is in the form [ [[top-left, top-right, bottom-right, bottom-left], text, confidence]]
    bbox, text, score = t
    l_bbox = bbox[0][0]  # x1
    l_bbox1 = bbox[0][1]  # y1
    r_bbox = bbox[2][0]  # x2
    r_bbox1 = bbox[2][1]  # y2
    confidence_scores.append(score)

    cv2.rectangle(img, (int(l_bbox), int(l_bbox1)), (int(r_bbox), int(r_bbox1)), (0, 255, 0),2)
    cv2.putText(img, text, (int(l_bbox), int(l_bbox1)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0 ,0), 2)

average_confidence = sum(confidence_scores) / len(confidence_scores)
print(f"Average Confidence Score: {average_confidence}")
cv2.imshow("Output", img)
cv2.waitKey(0)