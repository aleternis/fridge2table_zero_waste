from crewai.tools import BaseTool, tool
from typing import Type
from pydantic import BaseModel, Field
import json
from PIL import Image
import google.generativeai as genai
import os
import PIL.Image




class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
    


# Initialize Gemini API

class ImageToTextTool:
    """
    A tool that extracts text from images using Google Gemini Pro Vision.
    """


    @staticmethod
    @tool("identify_fridge_items")
    def identify_fridge_items(image_path: str) -> str:
        """
        Identifies food items in a fridge photo using Gemini Pro Vision.

        Args:
            image_path (str): Path to the fridge image.

        Returns:
            str: A detailed list of identified food items, including estimated quantities if possible.
        """
        try:
            # Open the image file
            img_data = PIL.Image.open(image_path)

            # Load Gemini Vision model
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            # English system prompt, focused on fridge contents
            prompt = (
                "Identify and list all visible food items in this fridge photo. "
                "For each item, estimate the quantity or count if possible. "
                "Return the result as a clear and structured list (preferably JSON or YAML format). "
                "Do not mention items that are not food or drink."
            )
            print("[DEBUG] Calling Gemini Vision model with prompt and image data...")
            response = model.generate_content(
                contents=[prompt, img_data]
            )
            print("[DEBUG] Gemini Vision model response received.")

            return response.text if response.text else "No items identified."

        except Exception as e:
            print("[ERROR] LLM call failed:", e)
            return f"Error processing the image: {str(e)}"
