#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from fridge2table_zero_waste.crew import Fridge2TableZeroWaste

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        "fridge_photo": r"C:\Users\alete\Documentos\AIAgents\fridge2table_zero_waste\fridge2table_zero_waste\knowledge\fridge.jpg"
    }
    
    try:
        Fridge2TableZeroWaste().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
