from PIL import Image
import numpy as np
import argparse
import cv2
import pytesseract
import glob
import re
from Graph import Graph

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
        # nodes
        nodes = self.find_nodes()

        # dictionary from node path name to node coordinates
        nodes_path_coord_dict = self.crop_nodes(nodes)

        # self.crop_nodes(nodes)

        # dictionary from node path name to node label
        G, nodes_coord_name_dict = self.read_text()

        # edges coordinates
        edges = self.find_edges()

        E = self.connect_nodes(nodes_path_coord_dict, nodes_coord_name_dict, edges)

        # node dictionaries
        if preview:
            print("\nnodes path coord dict")
            for key in nodes_path_coord_dict:
                print(key, nodes_path_coord_dict[key])

            print("\nnodes coord name dict")
            for key in nodes_coord_name_dict:
                print(key, nodes_coord_name_dict[key])

        graph = Graph()
        for g in G:
            graph.add_vertex(g)
        for e in E:
            if (len(set(e)) == 2):
                graph.add_edge(e)
        print("nodes: ", graph.vertices())
        print("edges: ", graph.edges())

    # https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/
    # read node name inside all nodes
    def read_text(self):

        nodes_text_dict = {}

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

            G = []

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

                if preview:
                    print("text: ", text)

                nodes_text_dict[node_path] = str(text)

                # Appending the text into file
                file.write(text)
                file.write("\n")

                # Close the file
                file.close

        G = nodes_text_dict.values()
        return G, nodes_text_dict

    # https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    # find nodes in graph
    def find_nodes(self):

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
        nodes_paths_dict = {}

        for (x, y, r) in circles:

            # bottom left
            x0 = x - r
            y0 = y - r

            # top right
            x1 = x + r
            y1 = y + r

            img = cv2.imread(self.image_path)
            crop_img = img[y0:y1, x0:x1]

            node_name = "{0}_{1}_{2}".format(x, y, r)
            node_output_path = "outputs/nodes/{0}.png".format(node_name)

            # view node cropped
            if (preview):
                cv2.imshow(node_output_path, crop_img)
                cv2.waitKey(0)

            # save image
            cv2.imwrite(node_output_path, crop_img)

            # associate image of node (path name) and coordinates
            nodes_paths_dict[node_name] = (x, y, r)

        return nodes_paths_dict

    # RGB to Gray
    def grayify(self, image):
        # save grayscale image
        if (len(image.shape)==3):
            image = cv2.cvtColor(np.float32(image), cv2.COLOR_BGR2GRAY)
        return image

    # https://www.geeksforgeeks.org/line-detection-python-opencv-houghline-method/
    # find edges in graph
    def find_edges(self):
        img = self.image
        gray = self.gray

        edges = cv2.Canny(gray, 75, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, maxLineGap=25)

        # TO-DO: adjustable MaxLineGap

        edges_arr = []

        # https://www.tutorialspoint.com/line-detection-in-python-with-opencv
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 128), 1)

            if preview:
                # cv2.imshow("linesEdges", edges)
                cv2.imshow("linesDetected", img)
                cv2.waitKey(0)

            edges_arr.append([(x1, y1), (x2, y2)])

        # print(edges_arr)
        return edges_arr

    def connect_nodes(self, name_coord, name_label, edges):
        if preview:
            print("\nname_coord dict")
            for key in name_coord:
                print(key, name_coord[key])

            print("\nname_label dict")
            for key in name_label:
                print(key, name_label[key])

            print("\nedges")
            for edge in edges:
                print(edge)

        E = []
        threshold = 10
        for edge in edges:
            # endpoint nodes
            e  = []
            for (x_coord, y_coord) in edge:

                for key in name_coord:
                    x, y, r = name_coord[key]
                    x_range = range(x - r - threshold, x + r + threshold)
                    y_range = range(y - r - threshold, y + r + threshold)
                    if ((x_coord in x_range) and (y_coord in y_range)):
                        e.append(key)

                    if preview: # else:
                        if ((x_coord in x_range) or (y_coord in y_range)):
                            print("{0} in x range: {1} - {2} (difference of {3})".format(x_coord,
                                                                                         x - r,
                                                                                         x + r,
                                                                                         x_coord - (x + r) if (x_coord > x + r) else (x - r) - x_coord))
                            print("{0} in y range: {1} - {2} (difference of {3})".format(y_coord,
                                                                                         y - r,
                                                                                         y + r,
                                                                                         y_coord - (y + r) if (y_coord > y + r) else (y - r) - y_coord))
                            print("{0}, {1}".format( "T" if (x_coord in x_range) else "F",  "T" if (y_coord in y_range) else "F"))
                            print('\n')

            # add edges with two endpoins in nodes to E
            if (len(e) == 2):
                # print(type(name_label)) # .get(e))
                E.append(e)

        E_names = []
        for edge in E:
            left_node = edge[0]
            right_node = edge[1]

            left_node = str(name_label[left_node])
            right_node = str(name_label[right_node])

            E_names.append([left_node, right_node])

        return E_names