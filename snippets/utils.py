from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings


def generate_result_image(result, score):

    template_path = os.path.join(
        settings.BASE_DIR,
        "static/images/result_template.png"
    )

    image = Image.open(template_path)

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "arial.ttf",
        60
    )

    draw.text((400, 300), result, fill="black", font=font)

    draw.text((400, 500), f"{score}%", fill="black", font=font)

    output_path = os.path.join(
        settings.MEDIA_ROOT,
        "result.png"
    )

    image.save(output_path)

    return output_path

def calculate_level(xp):
    return xp // 100 + 1