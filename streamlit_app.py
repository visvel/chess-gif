import streamlit as st
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import tempfile

# Helper functions
def chess_to_pixel(square, img_width, img_height):
    column = ord(square[0].lower()) - ord('a')
    row = 8 - int(square[1])
    x = (column + 0.5) * img_width / 8
    y = (row + 0.5) * img_height / 8
    return int(x), int(y)

def draw_arrowhead(draw, start, end, color, size, angle):
    from math import atan2, sin, cos, radians
    line_angle = atan2(end[1] - start[1], end[0] - start[0])
    left_angle = line_angle + radians(180 - angle)
    right_angle = line_angle - radians(180 - angle)
    left_x = end[0] + size * cos(left_angle)
    left_y = end[1] + size * sin(left_angle)
    right_x = end[0] + size * cos(right_angle)
    right_y = end[1] + size * sin(right_angle)
    draw.line([end, (left_x, left_y)], fill=color, width=4)
    draw.line([end, (right_x, right_y)], fill=color, width=4)

def create_elegant_gif(image, lines):
    line_colors = ["red", "blue", "green", "orange", "purple", "cyan", "magenta", "yellow"]
    img_width, img_height = image.size
    resized_width = img_width // 2
    resized_height = img_height // 2
    resized_image = image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(resized_image)
    watermark_text = ""
    font_size = 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    watermark_position = (resized_width - text_width - 10, 10)
    draw.text(watermark_position, watermark_text, font=font, fill=(255, 255, 255, 128))

    frames = [resized_image.copy()]
    cumulative_frame = resized_image.copy()
    draw = ImageDraw.Draw(cumulative_frame)

    for i, line in enumerate(lines):
        start_square, end_square = line[:2], line[2:]
        start = chess_to_pixel(start_square, resized_width, resized_height)
        end = chess_to_pixel(end_square, resized_width, resized_height)
        color = line_colors[i % len(line_colors)]
        draw.line([start, end], fill=color, width=4)
        draw_arrowhead(draw, start, end, color, size=10, angle=30)
        frames.append(cumulative_frame.copy())

    frames.append(resized_image.copy())

    temp_gif = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
    frames[0].save(
        temp_gif.name,
        save_all=True,
        append_images=frames[1:],
        duration=2000,
        loop=0
    )
    return temp_gif.name

# Streamlit UI
st.title("Elegant Chess Line GIF Generator ✨")

uploaded_file = st.file_uploader("Upload your Image (PNG or JPEG)", type=["png", "jpg", "jpeg"])
lines_input = st.text_input("Enter chess lines (e.g., e2e4,d2d4)")

if uploaded_file and lines_input:
    try:
        image = Image.open(uploaded_file)
        lines = [line.strip() for line in lines_input.split(",")]
        st.info("Generating GIF, please wait...")

        gif_path = create_elegant_gif(image, lines)

        with open(gif_path, "rb") as f:
            gif_bytes = f.read()
            st.download_button(
                label="Download your GIF",
                data=gif_bytes,
                file_name="output.gif",
                mime="image/gif"
            )
            st.image(gif_bytes, caption="Preview of generated GIF", use_container_width=True)
    except Exception as e:
        st.error(f"Something went wrong: {e}")
