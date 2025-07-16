import sys
import os
import tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
from fridge2table_zero_waste.crew import Fridge2TableZeroWaste

st.set_page_config(page_title="Fridge2Table Zero Waste", page_icon=":bento_box:", layout="wide")
st.title("Fridge2Table Zero Waste")

uploaded_file = st.file_uploader("Upload a fridge photo...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    max_width = 350
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size)
    st.image(image, caption="Your fridge!", width=max_width)

    # Save uploaded image to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_file.read())
        image_path = tmp.name

    with st.spinner("Generating your personalized zero-waste meal plan..."):
        result = Fridge2TableZeroWaste().crew().kickoff(inputs={"fridge_photo": image_path})

    st.markdown(
        """
        <style>
        .zero-waste-title {
            font-size:2em;
            font-weight:bold;
            margin-bottom: 0.5em;
            margin-top: 0.2em;
            color: #308446;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="zero-waste-title">Your Zero Waste Meal Plan</div>', unsafe_allow_html=True)

    # Display markdown-rich output with all notes, formatting, etc.
    if isinstance(result, dict) and "raw" in result:
        st.markdown(result["raw"], unsafe_allow_html=True)
    else:
        st.markdown(str(result), unsafe_allow_html=True)

else:
    st.info("Please upload a fridge photo (jpg, jpeg, or png) to start analysis.")
