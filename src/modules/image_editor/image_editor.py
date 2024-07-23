from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont, ImageEnhance
import textwrap


class Templates:
    @staticmethod
    def image_with_text(image_file_path: str,
                        text: str,
                        output_path: str,
                        font_path: str = "../assets/fonts/Montserrat-ExtraBold.ttf",
                        font_size: int = 48,
                        image_brightness: float = 0.5,
                        textwrap_width: int = 24) -> str:
        """
        Create an image with text in the center.
        :param image_file_path: Input image file path
        :param text: Text to be written on the image
        :param output_path: Output path for the image
        :param font_path: Font path
        :param font_size: Font size
        :param image_brightness: Image brightness
        :param textwrap_width: Text wrap width
        :return:
        """
        file_name = image_file_path.split("/")[-1]
        image = Image.open(image_file_path)

        font = ImageFont.truetype(font_path, font_size)
        enhancer = ImageEnhance.Brightness(image)
        # to reduce brightness by 50%, use factor 0.5
        image = enhancer.enhance(image_brightness)
        draw = ImageDraw.Draw(image)

        lines = textwrap.wrap(text, width=textwrap_width)

        max_width = 0
        total_height = 0
        for line in lines:
            width, height = draw.textsize(line, font=font)
            max_width = max(max_width, width)
            total_height += height

        x = (image.width - max_width) // 2
        y = (image.height - total_height) // 2

        line_heights = []
        for line in lines:
            width, height = draw.textsize(line, font=font)
            line_heights.append(height)

        line_y = y
        for i in range(len(lines)):
            line_x = x + (max_width - draw.textsize(lines[i], font=font)[0]) // 2
            draw.text((line_x, line_y), lines[i], font=font)
            line_y += line_heights[i]

        new_name = file_name.split(".")[0] + ".png"
        file_location = output_path + new_name
        image.save(file_location)

        return file_location

# def create_multiple(text, image_file_name):
#     fonts = ["../assets/fonts/Montserrat-ExtraBold.ttf",
#              "../assets/fonts/Montserrat-BoldItalic.ttf",
#              "../assets/fonts/Montserrat-Light.ttf"]
#     font_sizes = [36, 48, 54]
#     image_brightness = [0.3, 0.5, 0.7]
#     index = 0
#     for f in fonts:
#         for s in font_sizes:
#             for b in image_brightness:
#                 create_image_text(image_file_path='../assets/images/' + image_file_name, image_name="marcus1.png",
#                                   font_path=f, font_size=s, text=text, index=index, output_path=, image_brightness=b)
#                 index += 1
