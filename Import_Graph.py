from PIL import Image
import numpy as np
import argparse
import cv2
import pytesseract
import glob
import re

### Settings ###

# True when debugging
preview = False

# True if nodes are labeled with numbers solely
digit = True


class Import_Graph:
    def __init__(self, image_path):
        self.image_path = image_path
        self.text = "outputs/text"
        self.node_paths = 'outputs/nodes/'
        self.node_names = 'outputs/nodes/names/'

        image = cv2.imread(image_path, 0)
        self.image = image
        self.gray = self.grayify(image)

    # main function
    def import_graph(self):
        circles = self.find_circles()
        self.crop_nodes(circles)
        self.read_text()

    # https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/
    # read node name inside all nodes
    def read_text(self):

        for node in glob.glob(self.node_paths + '*.png'):
            img = cv2.imread(node, 0)
            gray = self.grayify(img)

            node_path = node.split('/')[-1]
            node_path = node_path.split('.')[0]
            text_file = self.node_names + node_path + '.txt'

            # Performing OTSU threshold
            ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

            # Specify structure shape and kernel size.
            # Kernel size increases or decreases the area of the rectangle to be detected.
            # A smaller value like (10, 10) will detect each word instead of a sentence.
            rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

            # Appplying dilation on the threshold image
            dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)

            # Finding contours
            _, contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # Creating a copy of image
            im2 = img.copy()

            # A text file is created and flushed
            file = open(text_file, "w+")
            file.write("")
            file.close()

            # Looping through the identified contours
            # Then rectangular part is cropped and passed on to pytesseract for extracting text from it
            # Extracted text is then written into the text file
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)

                # Drawing a rectangle on copied image
                rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Cropping the text block for giving input to OCR
                cropped = im2[y:y + h, x:x + w]

                # cv2.imshow("cropped", cropped)
                # cv2.waitKey(0)

                # Open the file in append mode
                file = open(text_file, "a")

                # Apply OCR on the cropped image
                text = pytesseract.image_to_string(cropped, config='--psm 10')
                if digit:
                    text = re.sub("[^0-9^.]", "", text)
                else:
                    text = re.sub("[^0-9A-Za-z^.]", "", text)
                print("text: ", text)

                # Appending the text into file
                file.write(text)
                file.write("\n")

                # Close the file
                file.close

    # https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    # find nodes in graph
    def find_circles(self):

        gray = self.gray
        output = gray.copy()

        # TO-DO: Allow user to adjust params (up, down) till all circles selected

        # detect circles in the image
        circles = cv2.HoughCircles(gray,
                                   cv2.HOUGH_GRADIENT,
                                   1,
                                   20,
                                   param1=30,
                                   param2=15,
                                   minRadius=12,
                                   maxRadius=30)

        # ensure at least some circles were found
        if circles is not None:

            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:

                # draw the circle in the output image
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)

                # draw a rectangle corresponding to the center of the circle
                # cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # show the output image
            if (preview):
                cv2.imshow("output", np.hstack([gray, output]))
                cv2.waitKey(0)

        return circles

    # crop nodes from graph
    def crop_nodes(self, circles):
        for (x, y, r) in circles:

            # bottom left
            x0 = x - r
            y0 = y - r

            # top right
            x1 = x + r
            y1 = y + r

            img = cv2.imread(self.image_path)
            crop_img = img[y0:y1, x0:x1]

            if (preview):
                cv2.imshow("outputs/nodes/{0}_{1}_{2}.png".format(x, y, r), crop_img)
                cv2.waitKey(0)

            cv2.imwrite("outputs/nodes/{0}_{1}_{2}.png".format(x, y, r), crop_img)

    # RGB to Gray
    def grayify(self, image):
        # save grayscale image
        if (len(image.shape)==3):
            image = cv2.cvtColor(np.float32(image), cv2.COLOR_BGR2GRAY)
        return image
