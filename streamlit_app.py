from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

st.title("Welcome")
st.header("This is Image generation Test") 

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])
image_bytes = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image.thumbnail((512, 512))
    st.image(image, caption="Uploaded Image", use_container_width=True)
    import io
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

with st.form("image_form", clear_on_submit=True):

    prompt = st.text_input(label="What do you want to do with image?", placeholder="e.g., Describe this image or Generate a caption")
    submit = st.form_submit_button("Submit")

    if submit and uploaded_file is not None and image_bytes is not None:
        st.markdown(f"**Your Prompt:** `{prompt}`  \n**Response received from Gemini API:**")
        with st.spinner("Waiting for Gemini API response..."):
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg',
                    ),
                    prompt
                ]
            )
        # Check if response has text
        if hasattr(response, 'text') and response.text:
            st.write(response.text)
        elif hasattr(response, 'inline_data'):
            # Handle inline data if it exists
            for part in response.inline_data:
                if part.image:
                    st.image(part.image, caption="Generated Image")
                else:
                    st.write(part.text)  # Handle other text parts if necessary
        else:
            st.write("No response text or inline data received.")
        
