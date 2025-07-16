import streamlit as st
from PIL import Image
import tempfile
import os
import re
import sys
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
    sys.modules["sqlite3.dbapi2"] = pysqlite3.dbapi2
except ImportError:
    pass  # pysqlite3 not installed, fallback to system sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from dotenv import load_dotenv
#load_dotenv()

from fridge2table_zero_waste.crew import Fridge2TableZeroWaste

# ---------- Custom CSS & Layout -----------
st.set_page_config(page_title="Fridge2Table Zero Waste", layout="wide")
st.markdown("""
    <style>
    .hero { display: flex; align-items: center; gap: 1.2rem; margin-bottom: 2rem; margin-top: 0rem !important; }
    .hero-icon { font-size: 2.7rem; margin-right: 0.2rem; margin-top: -4px; }
    .hero-content h1 { font-size: 2.4rem; font-weight: 800; margin-bottom: 0.3rem; margin-top: 0.1rem; color: #247144; letter-spacing: -1px; }
    .hero-content p { font-size: 1.2rem; color: #397150; margin-top: 0; margin-bottom: 0; font-weight: 500; }
    .card { }
    .stButton button { color: #fff; background: linear-gradient(90deg,#37c978 30%,#247144 100%); font-weight: 700; border-radius: 0.7em; padding: 0.5em 2em; margin-top: 1.2em; margin-bottom: 0.2em; border: none; }
    #MainMenu, footer {visibility: hidden;}
    .feedback-section { margin-top: 2.5em; text-align: center; font-size: 1.15rem; color: #247144;}
    .prioritization-card { background: #e8f6ef; border-left: 6px solid #54c27d; border-radius: 1.1em; margin-top: 1.6em; margin-bottom: 2em; padding: 1.2em 1.2em 1.2em 1.7em; font-size: 1.12em; color: #247144; font-weight: 500; box-shadow: 0 2px 10px rgba(36,113,68,0.07);}
    /* ----------- REMOVE BLANK BARS AT TOP ----------- */


    </style>
""", unsafe_allow_html=True)
    #.card { background: var(--background-color, #18191A); border-radius: 1.25rem; padding: 2.1rem 1.6rem 1.1rem 1.6rem; margin-bottom: 1.2rem; box-shadow: 0 2px 18px 0 rgba(0,0,0,0.07); border: 1.5px solid #e2f6e9; }

# ---------- Hero Section -----------
st.markdown("""
<div class="hero">
    <span class="hero-icon">🥗</span>
    <div class="hero-content">
        <h1>Fridge2Table <span style="color:#54c27d;">Zero Waste</span></h1>
        <p>Analyze your fridge photo and get a smart, waste-cutting 7-day meal plan. Eat well, save money, and help the planet! 🌍</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Columns ----------
left_col, center_col, right_col = st.columns([1.1, 1.7, 1.1], gap="large")

SAMPLE_IMAGE_PATH = "sample_fridge.jpg"
def get_sample_image():
    if os.path.exists(SAMPLE_IMAGE_PATH):
        return Image.open(SAMPLE_IMAGE_PATH), SAMPLE_IMAGE_PATH
    img = Image.new('RGB', (480, 300), color=(240, 255, 248))
    return img, None

# ---------- Left Column: Upload -----------
with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 📷 Upload Your Fridge Photo")
    uploaded_file = st.file_uploader(
        "Choose a photo of your fridge to begin",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        help="Take a clear, well-lit photo of the inside of your fridge."
    )

    use_sample = False
    uploaded_image_path = None
    image = None
    sample_image_path = None

    if uploaded_file is None:
        if st.button("Try a Sample Fridge Photo", use_container_width=True):
            use_sample = True
            image, sample_image_path = get_sample_image()
    else:
        image = Image.open(uploaded_file)
        uploaded_file.seek(0)  # Rewind to start!
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(uploaded_file.read())
            uploaded_image_path = tmp.name

    # Preview fridge image
    if uploaded_file or use_sample:
        st.markdown("##### Preview:")
        st.image(
            image,
            use_container_width=True,
            output_format="JPEG",
            channels="RGB",
            caption="Your Fridge",
            clamp=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Center Column: Meal Plan Tabs ----------
with center_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🍽️ Your Zero Waste Meal Plan")
    prioritization_note = ""
    zero_waste_tips_md = ""
    days = []

    if uploaded_file or use_sample:
        photo_path = uploaded_image_path if uploaded_file else sample_image_path
        with st.spinner("Analyzing your fridge and building your meal plan..."):
            result = Fridge2TableZeroWaste().crew().kickoff(inputs={"fridge_photo": photo_path})

        # --- Parse output ---
        if isinstance(result, dict) and "raw" in result:
            mealplan_md = result["raw"]
        else:
            mealplan_md = str(result)

        # 1. Extract Prioritization Note (remove from markdown)
        prio_match = re.search(r"\*\*?Prioritization Note:?[\*\s]*:?(.+?)(?=\n\n|##|$)", mealplan_md, re.IGNORECASE | re.DOTALL)
        if prio_match:
            prioritization_note = prio_match.group(1).strip()
            mealplan_md = mealplan_md.replace(prio_match.group(0), "")

        # 2. Extract Zero-Waste Tips Section (remove from markdown)
        tips_match = re.search(r"##+\s*Zero-Waste Tips.*?(\n[\s\S]*)", mealplan_md, re.IGNORECASE)
        if tips_match:
            zero_waste_tips_md = tips_match.group(1).strip()
            mealplan_md = mealplan_md[:tips_match.start()]  # Remove tips section from center col

        # 3. Split markdown into days (tabs)
        split = re.split(r"(?:^|\n)(?:##+\s*)?Day\s*\d+[:\s]*", mealplan_md, flags=re.IGNORECASE)
        headers = re.findall(r"(?:^|\n)(?:##+\s*)?Day\s*\d+[:\s]*", mealplan_md, flags=re.IGNORECASE)
        plan_head = ""
        if split and len(split) > 1:
            plan_head = split[0]
            for i in range(1, len(split)):
                title = headers[i-1].strip() if i-1 < len(headers) else f"Day {i}"
                day_md = split[i]
                days.append((title, day_md))
        else:
            plan_head = mealplan_md  # fallback

        # Show meal plan only (tabs for each day)
        if days:
            tabs = st.tabs([d[0] for d in days])
            for i, (title, body) in enumerate(days):
                with tabs[i]:
                    # Highlight "Zero-Waste Tip:" (per day) as info callout
                    tip_lines = []
                    rest = []
                    for line in body.splitlines():
                        if line.strip().lower().startswith("zero-waste tip"):
                            tip_lines.append(line.strip())
                        else:
                            rest.append(line)
                    md = "\n".join(rest).strip()
                    if md:
                        st.markdown(md, unsafe_allow_html=True)
                    for tip in tip_lines:
                        tip_txt = tip.replace("Zero-Waste Tip:", "").strip(" :-")
                        st.info(f"Zero-Waste Tip: {tip_txt}", icon="♻️")
        else:
            st.markdown(mealplan_md, unsafe_allow_html=True)
    else:
        st.markdown("#### 👈 Upload a photo or use the sample to get your meal plan.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Right Column: Prioritization Note + Zero-Waste Tips ----------
with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 🟢 Prioritization Note", unsafe_allow_html=True)
    if prioritization_note:
        st.write(prioritization_note)
    else:
        st.write("Prioritization info about which ingredients to use first will appear here after analysis.")

    if zero_waste_tips_md:
        st.markdown("---")
        st.markdown("#### ♻️ Zero-Waste Tips & Notes")
        st.markdown(zero_waste_tips_md, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)