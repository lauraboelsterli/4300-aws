'''
using opencv for image preprocessing for keras
'''
import keras_ocr
import matplotlib.pyplot as plt
import cv2

# using their pretrained model 
pipeline = keras_ocr.pipeline.Pipeline()
# image_path = 'documents/tabular.tiff'
image_path = 'OCR_testing/documents/structured_text.png'
image = cv2.imread(image_path)
# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding for binarization
_, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# Convert the preprocessed image to RGB format for Keras OCR
binary_image_rgb = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)


prediction_groups = pipeline.recognize([binary_image_rgb])


for text, box in prediction_groups[0]:
    print(f"{text}")


fig, ax = plt.subplots(figsize=(15, 5))
keras_ocr.tools.drawAnnotations(image=binary_image_rgb, predictions=prediction_groups[0], ax=ax)
plt.show()






