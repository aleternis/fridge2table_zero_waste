#!/usr/bin/env python
try:
    import pysqlite3
    import sys
    sys.modules["sqlite3"] = pysqlite3
except Exception:
    pass

import sys
import warnings

from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import warnings
from datetime import datetime
from fridge2table_zero_waste.crew import Fridge2TableZeroWaste

from fridge2table_zero_waste.crew import Fridge2TableZeroWaste

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():


    HARDCODED_IMAGE_PATH = r"C:\Users\alete\Documentos\AIAgents\fridge2table_zero_waste\fridge2table_zero_waste\knowledge\fridge.jpg"

    if st.button("Run Fridge Analysis"):
        with st.spinner("Running CrewAI..."):
            result = Fridge2TableZeroWaste().crew().kickoff(inputs={"fridge_photo": HARDCODED_IMAGE_PATH})
        st.subheader("CrewAI Output")
        st.write(result)

    #"""
    #Run the crew.
    #"""
    #inputs = {
    #    "fridge_photo": r"C:\Users\alete\Documentos\AIAgents\fridge2table_zero_waste\fridge2table_zero_waste\knowledge\fridge.jpg"
    #}
    
    #try:
    #    Fridge2TableZeroWaste().crew().kickoff(inputs=inputs)
    #except Exception as e:
    #    raise Exception(f"An error occurred while running the crew: {e}")
