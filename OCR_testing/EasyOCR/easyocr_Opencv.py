'''
with some openCV processing the average text detection confidence score goes up 
'''
import cv2
import easyocr
import matplotlib.pyplot as plt

# image_path = 'documents/tabular.tiff'  
image_path = 'OCR_testing/documents/structured_text.png'  
image = cv2.imread(image_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

_, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

reader = easyocr.Reader(['en'])
ocr_result = reader.readtext(binary_image, detail=1)

extracted_text = [detection[1] for detection in ocr_result]
print("Extracted Text from Table:", extracted_text)


confidence_scores = []

for detection in ocr_result:
    # Unpack the detection result
    bbox, text, score = detection
    # print(text)

    # Extract the individual coordinates from the bounding box
    l_bbox = bbox[0][0]  # x1
    l_bbox1 = bbox[0][1]  # y1
    r_bbox = bbox[2][0]  # x2
    r_bbox1 = bbox[2][1]  # y2
    # Append the confidence score (score calcualted per word) to the list
    confidence_scores.append(score)

    # Plot the image with bounding boxes to verify detection visually
    # Draw the rectangle using integer coordinates
    cv2.rectangle(image, (int(l_bbox), int(l_bbox1)), (int(r_bbox), int(r_bbox1)), (0, 255, 0), 2)
    # Put the text on the image
    cv2.putText(image, text, (int(l_bbox), int(l_bbox1)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)


average_confidence = sum(confidence_scores) / len(confidence_scores)
print(f"Average Confidence Score: {average_confidence}")
plt.figure(figsize=(10, 10))
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()
