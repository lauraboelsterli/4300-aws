'''
followed this link: https://keras-ocr.readthedocs.io/en/latest/examples/using_pretrained_models.html
did not preprocess the image before extraction'''
import keras_ocr
import matplotlib.pyplot as plt

# using their pretrained model 
pipeline = keras_ocr.pipeline.Pipeline()
# image_path = 'documents/tabular.tiff'
image_path = 'OCR_testing/documents/structured_text.png'
image = keras_ocr.tools.read(image_path)

# ocr
prediction_groups = pipeline.recognize([image])
# Print ttext
for text, box in prediction_groups[0]:
    print(f"{text}")

# Plotting preds
fig, ax = plt.subplots(figsize=(15, 5))

# warning!! these annotations are messy to read 
# but you can customize fig size or plot it and thenjust change the dimensions of image on pop-up browser
# if want to check soley the output, then uncomment the text print statament from the prediction group variable  
keras_ocr.tools.drawAnnotations(image=image, predictions=prediction_groups[0], ax=ax)

plt.show()






