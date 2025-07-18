
import os
from google.adk.agents import Agent
from PIL import Image
from io import BytesIO
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def describe_image_with_gpt4_vision(image: bytes) -> str:
    """
    Uses GPT-4 Vision to describe the contents of the given image.
    
    Args:
        image (bytes): Image file in binary format.
        
    Returns:
        A textual description of the image.
    """
    try:
        img = Image.open(BytesIO(image))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_image = buffered.getvalue()

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Describe the plant in this image. Be specific if possible."},
                    {"type": "image_url", "image_url": {
                        "url": "data:image/png;base64," + base64_image.decode("latin1")
                    }}
                ]}
            ],
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error analyzing image with GPT-4-Vision: {e}"
    

image_recognition = Agent(
    name="image_recognition",
    model="gpt-4-vision-preview",  
    description=(
        "An AI botanist that, given an image file path, loads the image and "
        "identifies the plant name."
    ),
    instruction=(
        "You get one input key:\n"
        "  • image_path: a filesystem path to the plant photo\n\n"
        "Step 1) Call the tool `load_image_bytes` with that path.  \n"
        "Step 2) Take the returned `image_bytes` and identify the plant.  \n"
        "Output exactly one line:\n"
        "    The name of the plant is: <common name>\n"
        "If you can’t tell, say exactly:\n"
        "    I’m not sure what plant this is.\n\n"
        "Don’t output JSON or extra text—just that line."
    ),
    tools=[describe_image_with_gpt4_vision]
)
