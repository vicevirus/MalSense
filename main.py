import streamlit as st
import re
import requests
import base64
from openai import OpenAI
from PIL import Image
import io
import json
from typing import Tuple

client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])


def check_content(content, is_image=False):
    prompt = {
        "role":
        "system",
        "content":
        "You are a very strict assistant. You are help to help assist the user if the content or image that the user showing is malicious, phishing, scams, ponzi scams or anything similar. Most of the time it could be too good to be true, if it even seem a little bit of that to good to be true, give out points. Reply in JSON format with points that makes it suspicious and rating of sus 0/100. Never, never give me in markdown format. If the content is not suspicious, reply with This doesnt seems suspicious"
    }
    example_response = {
        "role": "assistant",
        "content": "{'points': ['point1', 'point2', 'point3'], 'rating': 70}"
    }
    user_content = {
        "role":
        "user",
        "content":
        content if not is_image else [{
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{content}"
            }
        }]
    }
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[prompt, example_response, user_content],
        max_tokens=300,
    )
    return completion.choices[0].message.content


def extract_links(content):
    return re.findall(r'https?://\S+', content)


def scan_url(url):
    urlscan_api_key = st.secrets['URLSCAN_API_KEY']
    headers = {'API-Key': urlscan_api_key, 'Content-Type': 'application/json'}
    data = {"url": url, "visibility": "public"}
    try:
        response = requests.post('https://urlscan.io/api/v1/scan/',
                                 headers=headers,
                                 json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error scanning URL: {str(e)}"


def process_image(image_data, max_size: int) -> Tuple[str, int]:
    with Image.open(image_data) as image:
        width, height = image.size
        mimetype = image.get_format_mimetype()
        if mimetype == "image/png" and width <= max_size and height <= max_size:
            encoded_image = base64.b64encode(
                image_data.getvalue()).decode('utf-8')
            return (encoded_image, max(width, height))
        else:
            resized_image = resize_image(image, max_size)
            png_image = convert_to_png(resized_image)
            return (base64.b64encode(png_image).decode('utf-8'),
                    max(width, height))


def resize_image(image: Image.Image, max_dimension: int) -> Image.Image:
    width, height = image.size
    if image.mode == "P":
        if "transparency" in image.info:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        image = image.resize((new_width, new_height), Image.LANCZOS)
    return image


def convert_to_png(image: Image.Image) -> bytes:
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()


st.title('Sus Content Checker')
st.image(
    'https://static.wikia.nocookie.net/amonguslogic/images/a/a5/SUS_thumbnail.jpg'
)

option = st.selectbox("Select the type of content to check:",
                      ["Text", "Image"])

if option == "Text":
    content = st.text_area("Enter the text to check", height=250)
elif option == "Image":
    uploaded_file = st.file_uploader("Upload an image",
                                     type=["jpg", "png", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=image.format)
        image_bytes.seek(0)
        image_base64, max_dim = process_image(image_bytes, max_size=1024)
        st.image(uploaded_file,
                 caption='Uploaded Image',
                 use_column_width=True)

if st.button("Check for sus content"):
    if option == "Text" and content:
        result = check_content(content)
    elif option == "Image" and uploaded_file:
        result = check_content(image_base64, is_image=True)

    try:

        jsonResult = json.loads(result)

        if "points" in jsonResult and jsonResult["points"]:
            st.markdown("## Detected Points of Suspicion:")
            for point in jsonResult["points"]:
                st.markdown(f"- {point}")
            percentage_suspicion = min(len(jsonResult["points"]) * 20, 100)
            st.markdown("## Sus percentage:")
            st.metric(label="Suspicion Level",
                      value=f"{percentage_suspicion}%",
                      delta=None)
            st.image(
                'https://www.coque-unique.com/boutique-img/coqueunique/produit/-impostor-among-us-45024-smartphone-small.jpg',
                width=100)
        else:
            st.markdown("**Our assistant didn't detect it as suspicious**")
            st.markdown("## Sus percentage:")
            st.metric(label="Suspicion Level", value="0%", delta=None)
            st.image(
                'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/da3c9d43-2638-4757-b3d0-b8d5d0dcd7c7/de548p5-b657cd2a-f663-4540-af13-54f395a585af.png/v1/fill/w_500,h_500,q_80,strp/thumbs_up_among_us_emote_by_dekatessera_de548p5-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NTAwIiwicGF0aCI6IlwvZlwvZGEzYzlkNDMtMjYzOC00NzU3LWIzZDAtYjhkNWQwZGNkN2M3XC9kZTU0OHA1LWI2NTdjZDJhLWY2NjMtNDU0MC1hZjEzLTU0ZjM5NWE1ODVhZi5wbmciLCJ3aWR0aCI6Ijw9NTAwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.bPkmSNldQyii1YMdT-Zko_wZsHgvex2PIIcDHqBcYsw',
                width=200)
    except json.JSONDecodeError:
        st.write("Uh.. nothing I guess?")

    if option == "Text":
        links = extract_links(content)
        if links:
            st.markdown("## Extracted Links:")
            for link in links:
                st.write(link)
                scan_result = scan_url(link)
                st.markdown('## We scanned the links for you with urlscan <3')
                st.write(scan_result['result'])
            st.markdown(
                "For further analysis, you can manually check the links on [VirusTotal](https://www.virustotal.com/) or [URLScan](https://urlscan.io/)."
            )
        else:
            st.markdown("## Extracted Links:")
            st.write("No links found.")
