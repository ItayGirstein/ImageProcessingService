from pathlib import Path
from matplotlib.image import imread, imsave
import random


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        try:
            self.path = Path(path)
            self.data = rgb2gray(imread(path)).tolist()

        except:
            raise RuntimeError()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j - 1] - row[j]))

            self.data[i] = res

    def rotate(self):
        height = len(self.data)
        width = len(self.data[0])
        result = []
        for i in range(height):
            temp_row = []
            for j in range(width):
                temp_row.append(self.data[i][j])
            result.append(temp_row)
        self.data = result

    def salt_n_pepper(self):
        height = len(self.data)
        width = len(self.data[0])
        for i in range(height):
            for j in range(width):
                rand = random.uniform(0, 1)
                if rand < 0.2:
                    self.data[i][j] = 255
                elif rand > 0.8:
                    self.data[i][j] = 0

    def concat(self, other_img, direction='horizontal'):
        # TODO remove the `raise` below, and write your implementation
        raise NotImplementedError()

    def segment(self):
        height = len(self.data)
        width = len(self.data[0])
        for i in range(height):
            for j in range(width):
                if j > 100:
                    self.data[i][j] = 255
                else:
                    self.data[i][j] = 0
