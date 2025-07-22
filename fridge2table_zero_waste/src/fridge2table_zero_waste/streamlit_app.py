try:
    import pysqlite3
    import sys
    sys.modules["sqlite3"] = pysqlite3
except Exception:
    pass

import streamlit as st
from PIL import Image
import tempfile
import os
import re
import sys
import io
from xhtml2pdf import pisa
import markdown as md_lib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fridge2table_zero_waste.crew import Fridge2TableZeroWaste

# ---------- Função PDF (Markdown para HTML) -----------
def generate_pdf_xhtml2pdf(mealplan_md, prioritization_note, zero_waste_tips_md):
    mealplan_html = md_lib.markdown(mealplan_md)
    zero_waste_tips_html = md_lib.markdown(zero_waste_tips_md) if zero_waste_tips_md else ""
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; }}
        h1 {{ color: #247144; }}
        h2 {{ color: #54c27d; margin-top: 18px; }}
        .section {{ margin-bottom: 16px; }}
    </style>
    </head>
    <body>
    <h1>Fridge2Table Zero Waste - Meal Plan</h1>
    <h2>Prioritization Note</h2>
    <div class="section">{prioritization_note}</div>
    <h2>Meal Plan</h2>
    <div class="section">{mealplan_html}</div>
    <h2>Zero-Waste Tips & Notes</h2>
    <div class="section">{zero_waste_tips_html}</div>
    </body>
    </html>
    """
    pdf_bytes = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=pdf_bytes)
    if pisa_status.err:
        return None
    return pdf_bytes.getvalue()

# ---------- Custom CSS & Layout -----------
st.set_page_config(page_title="Fridge2Table Zero Waste", layout="wide")
st.markdown("""<style>/* ... seu css ... */</style>""", unsafe_allow_html=True)
st.markdown("""
<div class="hero">
    <span class="hero-icon">🥗</span>
    <div class="hero-content">
        <h1>Fridge2Table <span style="color:#54c27d;">Zero Waste</span></h1>
        <p>Analyze your fridge photo and get a smart, waste-cutting 7-day meal plan. Eat well, save money, and help the planet! 🌍</p>
    </div>
</div>
""", unsafe_allow_html=True)

left_col, center_col, right_col = st.columns([1.1, 1.7, 1.1], gap="large")

# ---------- Sessão State para persistência ----------
if "mealplan_md" not in st.session_state:
    st.session_state.mealplan_md = ""
    st.session_state.prioritization_note = ""
    st.session_state.zero_waste_tips_md = ""
    st.session_state.days = []
    st.session_state.analysis_done = False

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

    uploaded_image_path = None
    image = None

    if uploaded_file:
        image = Image.open(uploaded_file)
        uploaded_file.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(uploaded_file.read())
            uploaded_image_path = tmp.name

        st.markdown("##### Preview:")
        st.image(
            image,
            use_container_width=True,
            output_format="JPEG",
            channels="RGB",
            caption="Your Fridge",
            clamp=True
        )

        # Executa análise só quando novo upload
        if not st.session_state.analysis_done or st.session_state.get("last_img_path", "") != uploaded_image_path:
            with st.spinner("Analyzing your fridge and building your meal plan..."):
                result = Fridge2TableZeroWaste().crew().kickoff(inputs={"fridge_photo": uploaded_image_path})

            # Parse output
            mealplan_md = result["raw"] if isinstance(result, dict) and "raw" in result else str(result)
            prioritization_note = ""
            zero_waste_tips_md = ""
            days = []

            prio_match = re.search(r"\*\*?Prioritization Note:?[\*\s]*:?(.+?)(?=\n\n|##|$)", mealplan_md, re.IGNORECASE | re.DOTALL)
            if prio_match:
                prioritization_note = prio_match.group(1).strip()
                mealplan_md = mealplan_md.replace(prio_match.group(0), "")

            tips_match = re.search(r"##+\s*Zero-Waste Tips.*?(\n[\s\S]*)", mealplan_md, re.IGNORECASE)
            if tips_match:
                zero_waste_tips_md = tips_match.group(1).strip()
                mealplan_md = mealplan_md[:tips_match.start()]

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
                plan_head = mealplan_md

            # Salva no session_state
            st.session_state.mealplan_md = mealplan_md
            st.session_state.prioritization_note = prioritization_note
            st.session_state.zero_waste_tips_md = zero_waste_tips_md
            st.session_state.days = days
            st.session_state.analysis_done = True
            st.session_state.last_img_path = uploaded_image_path

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Center Column: Meal Plan Tabs ----------
with center_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🍽️ Your Zero Waste Meal Plan")

    if st.session_state.analysis_done and st.session_state.mealplan_md:
        days = st.session_state.days
        mealplan_md = st.session_state.mealplan_md

        # Exibe as tabs por dia
        if days:
            tabs = st.tabs([d[0] for d in days])
            for i, (title, body) in enumerate(days):
                with tabs[i]:
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

        # Download PDF
        pdf_bytes = generate_pdf_xhtml2pdf(
            st.session_state.mealplan_md,
            st.session_state.prioritization_note,
            st.session_state.zero_waste_tips_md
        )
        if pdf_bytes:
            st.download_button(
                label="⬇️ Download Meal Plan as PDF",
                data=pdf_bytes,
                file_name="meal_plan.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Erro ao gerar o PDF. Tente novamente.")

    else:
        st.markdown("#### 👈 Upload a photo to get your meal plan.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Right Column: Prioritization Note + Zero-Waste Tips ----------
with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 🟢 Prioritization Note", unsafe_allow_html=True)
    if st.session_state.prioritization_note:
        st.write(st.session_state.prioritization_note)
    else:
        st.write("Prioritization info about which ingredients to use first will appear here after analysis.")

    if st.session_state.zero_waste_tips_md:
        st.markdown("---")
        st.markdown("#### ♻️ Zero-Waste Tips & Notes")
        st.markdown(st.session_state.zero_waste_tips_md, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
