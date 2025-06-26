import streamlit as st
import matplotlib.pyplot as plt
import datetime
import pickle
import numpy as np
from fpdf import FPDF
import base64
import os


# Page setup
st.set_page_config(page_title="❤️ Anemia Sense", layout="centered")

# Background and font styling
page_bg_img = f'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

[data-testid="stApp"] {{
background-image: url("https://static.vecteezy.com/system/resources/previews/004/987/898/large_2x/doctor-in-medical-lab-coat-with-a-stethoscope-doctor-in-hospital-background-with-copy-space-low-poly-wireframe-vector.jpg");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
color: #FF1493;
font-family: 'Poppins', sans-serif;
font-weight: bold;
}}

h1, h2, h3, h4, h5, h6, .stTitle, .stSubheader {{
    color: #FF1493 !important;
    font-family: 'Poppins', sans-serif;
    font-weight: bold !important;
}}

.stMarkdown h3 {{
    font-size: 50px !important;
    font-weight: bold !important;
    color: #FF1493 !important;
}}

label, div, p, span, .stMarkdown, .stTextInput label, .stSelectbox label {{
    font-family: 'Poppins', sans-serif;
    color: #FF1493 !important;
    font-weight: bold !important;
}}

button, .stButton > button {{
    background-color: #87CEFA !important;
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5em 1em;
}}

button:focus {{outline: none;}}
.stButton > button:hover {{
    background-color: #00BFFF !important;
}}

.next-button button {{
    background-color: lightgreen !important;
    color: black;
    font-weight: bold;
}}

.date-day-box {{
    position: fixed;
    top: 5px;
    left: 5px;
    background: rgba(255,255,255,0.3);
    border-radius: 8px;
    padding: 10px;
    font-weight: bold;
    color: #FF1493;
    z-index: 1000;
    font-size: 14px;
    line-height: 1.2;
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Load ML model
model = pickle.load(open("anemia_model.pkl", "rb"))

# Normal ranges (for bar color)
normal_ranges = {
    'Hemoglobin': {'Male': (13.5, 17.5), 'Female': (12.0, 15.5)},
    'MCH': (27, 33),
    'MCHC': (32, 36),
    'MCV': (80, 100)
}

# Initial state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.page = 'login'
    st.session_state.users = {'user': 'pass'}
    st.session_state.username = ''
    st.session_state.password = ''
    st.session_state.gender = ''
    st.session_state.Hemoglobin = None
    st.session_state.MCH = None
    st.session_state.MCHC = None
    st.session_state.MCV = None

def go_to(page):
    st.session_state.page = page

# Date and Day top-left
if st.session_state.logged_in:
    today = datetime.date.today()
    day_name = today.strftime('%A')
    st.markdown(f'<div class="date-day-box">{today.strftime("%Y-%m-%d")}<br>{day_name}</div>', unsafe_allow_html=True)

# Login or Signup
if not st.session_state.logged_in:
    if st.session_state.page == 'login':
        st.markdown("### ❤️ Anemia Sense")
        st.session_state.username = st.text_input("Username")
        st.session_state.password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if st.session_state.username in st.session_state.users and \
                   st.session_state.users[st.session_state.username] == st.session_state.password:
                    st.session_state.logged_in = True
                    st.session_state.page = 'gender'
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with col2:
            if st.button("Create Account"):
                st.session_state.page = 'signup'

    elif st.session_state.page == 'signup':
        st.markdown("### ❤️ Anemia Sense ~ Signup")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if new_user and new_pass:
                st.session_state.users[new_user] = new_pass
                st.success("Account created! Redirecting...")
                st.session_state.logged_in = True
                st.session_state.username = new_user
                st.session_state.page = 'gender'
                st.rerun()
            else:
                st.error("Enter both username and password.")

# Main Test Flow
elif st.session_state.logged_in:
    if st.session_state.page == 'gender':
        st.title("Gender")
        gender = st.radio("", ["Male", "Female"])
        if gender:
            st.session_state.gender = gender
        col1, col2 = st.columns([1, 1])
        with col1:
            st.button(" Back")
        with col2:
            if st.session_state.gender:
                st.button("Next ", on_click=lambda: go_to("hemoglobin"))

    elif st.session_state.page == 'hemoglobin':
        st.markdown("### Enter Hemoglobin (g/dL)")
        value = st.slider("Hemoglobin", 0.0, 100.0, 13.0, 0.1)
        if value:
            st.session_state.Hemoglobin = value
        col1, col2 = st.columns(2)
        with col1:
            st.button(" Back", on_click=lambda: go_to("gender"))
        with col2:
            if st.session_state.Hemoglobin:
                st.button("Next ", on_click=lambda: go_to("mch"))

    elif st.session_state.page == 'mch':
        st.markdown("### Enter MCH (pg)")
        value = st.slider("MCH", 0.0, 100.0, 27.0, 0.1)
        if value:
            st.session_state.MCH = value
        col1, col2 = st.columns(2)
        with col1:
            st.button(" Back", on_click=lambda: go_to("hemoglobin"))
        with col2:
            if st.session_state.MCH:
                st.button("Next ", on_click=lambda: go_to("mchc"))

    elif st.session_state.page == 'mchc':
        st.markdown("### Enter MCHC (g/dL)")
        value = st.slider("MCHC", 0.0, 100.0, 32.0, 0.1)
        if value:
            st.session_state.MCHC = value
        col1, col2 = st.columns(2)
        with col1:
            st.button(" Back", on_click=lambda: go_to("mch"))
        with col2:
            if st.session_state.MCHC:
                st.button("Next ", on_click=lambda: go_to("mcv"))

    elif st.session_state.page == 'mcv':
        st.markdown("### Enter MCV (fL)")
        value = st.slider("MCV", 0.0, 100.0, 80.0, 0.5)
        if value:
            st.session_state.MCV = value
        col1, col2 = st.columns(2)
        with col1:
            st.button(" Back", on_click=lambda: go_to("mchc"))
        with col2:
            if st.session_state.MCV:
                st.button("Next ", on_click=lambda: go_to("result"))
   

    elif st.session_state.page == 'result':
        st.markdown("<h2>📊 Anemia Test Results</h2>", unsafe_allow_html=True)
        gender = st.session_state.gender
        hemo = st.session_state.Hemoglobin
        mch = st.session_state.MCH
        mchc = st.session_state.MCHC
        mcv = st.session_state.MCV

        # Final prediction using ML model
        def get_result():
            gender_num = 1 if gender == 'Male' else 0
            input_data = np.array([[gender_num, hemo, mch, mchc, mcv]])
            prediction = model.predict(input_data)[0]
            if prediction == 1:
                return "Anemia Detected (ML Model)", "red"
            else:
                return "No Anemia (ML Model)", "green"

        result, color = get_result()
        st.success(f"Result: {result}")

        # PDF Report Generation
        def generate_pdf_report(username, gender, hemo, mch, mchc, mcv, result):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.set_text_color(255, 255, 255)  # white text
            pdf.set_fill_color(255, 20, 147)  # pink background for title
            pdf.cell(200, 10, txt="Anemia Sense Report", ln=True, align='C', fill=True)
            pdf.ln(10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt=f"Username: {username}", ln=True)
            pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
            pdf.cell(200, 10, txt=f"Hemoglobin: {hemo} g/dL", ln=True)
            pdf.cell(200, 10, txt=f"MCH: {mch} pg", ln=True)
            pdf.cell(200, 10, txt=f"MCHC: {mchc} g/dL", ln=True)
            pdf.cell(200, 10, txt=f"MCV: {mcv} fL", ln=True)
            pdf.ln(10)
            pdf.set_text_color(220, 50, 50)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt=f"Result: {result}", ln=True)
            pdf_path = "anemia_report.pdf"  # save to working directory
            pdf.output(pdf_path)
            return pdf_path

        # Generate and offer download (before chart)
        pdf_path = generate_pdf_report(
            username=st.session_state.username,
            gender=gender,
            hemo=hemo,
            mch=mch,
            mchc=mchc,
            mcv=mcv,
            result=result
        )

        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_link = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="anemia_report.pdf">📥 Download Anemia Report (PDF)</a>'
            st.markdown(pdf_link, unsafe_allow_html=True)

        # Bar Chart
        fig, ax = plt.subplots()
        labels = ['Hemoglobin', 'MCH', 'MCHC', 'MCV']
        values = [hemo, mch, mchc, mcv]
        colors = []

        for i, label in enumerate(labels):
            r = normal_ranges[label] if label != 'Hemoglobin' else normal_ranges[label][gender]
            if values[i] < r[0]:
                colors.append('orange')
            elif values[i] > r[1]:
                colors.append('red')
            else:
                colors.append('green')

        bars = ax.bar(labels, values, color=colors, edgecolor='black')
        for i, v in enumerate(values):
            ax.text(i, v + 0.5, str(round(v, 1)), ha='center', color='black', fontweight='bold')

        ax.set_ylabel('Values')
        ax.set_title(f"📊 Anemia Test Results - {result}")
        st.pyplot(fig)

        if st.button("Return to Gender"):
            go_to("gender")

