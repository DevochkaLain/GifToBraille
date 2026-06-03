from PIL import Image
import cv2
import numpy as np


class Generator:
    def _get_image_size(self, image):
        width = len(image[0])
        length = len(image)

        return width, length

    def _from_image_size_to_braille_size(self, width, length, base_width=90):
        ration = length / width

        braille_width = base_width
        braille_length = round(braille_width * ration / 2)

        braille_width = braille_width * 2
        braille_length = braille_length * 4

        return braille_width, braille_length

    def _resize_to_dots(self, image, target_width, target_height, block_size=9, c=5):
        img_array = np.array(image, dtype=np.uint8)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        resized = cv2.resize(gray, (target_width, target_height), interpolation=cv2.INTER_AREA)

        binary = cv2.adaptiveThreshold(
            resized, 1, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, block_size, c
        )
        return binary.tolist()

    def _dots_to_braille_symbol(self, dots):
        code = 0x2800

        for d in dots:
            code += 1 << (d - 1)

        return chr(code)

    def _dots_to_braille_image(self, dots_image):
        braille_image = ''
        braille_line = []

        dots_line = []

        length = len(dots_image)
        width = len(dots_image[0])

        braille_grid = [
            [1, 4],
            [2, 5],
            [3, 6],
            [7, 8]
        ]

        for l in range(0, length, 4):
            for w in range(0, width, 2):

                for _l in range(4):
                    for _w in range(2):
                        if dots_image[l+_l][w+_w]:
                            dot_number = braille_grid[_l][_w]
                            dots_line.append(dot_number)

                braille_symbol = self._dots_to_braille_symbol(dots_line)
                braille_line.append(braille_symbol)

                dots_line = []

            braille_image += ''.join(braille_line) + '<br>'
            braille_line = []

        return braille_image

    def image_to_braille_image(self, image):
        width, length = self._get_image_size(image)
        braille_width, braille_length = self._from_image_size_to_braille_size(width, length)

        dots_image = self._resize_to_dots(image, braille_width, braille_length)
        braille_image = self._dots_to_braille_image(dots_image)

        return braille_image

    def gif_to_braille_image(self, image_bytes):
        with Image.open(image_bytes) as img:
            try:
                i = 0
                while True:
                    img.seek(i)

                    frame_rgb = img.convert('RGB')
                    array_frame = np.array(frame_rgb)
                    braille_image = self.image_to_braille_image(array_frame)

                    yield braille_image

                    i += 1
            except EOFError:
                return
