import os
import openai
import dotenv
import gradio as gr
import logging
from dalle3 import Dalle
from swarms.models import OpenAI  


model = OpenAI(os.getenv("OPENAI_API_KEY"))
response = model("Generate")
cookie = os.getenv("DALLE_COOKIE")

# Initialize DALLE3 API
dalle = Dalle(cookie)
logging.basicConfig(level=logging.INFO)



accumulated_story = ""
favorite_panels = []


def generate_images_with_dalle(refined_prompt):
    dalle.create(refined_prompt)
    urls = dalle.get_urls()
    return urls

def generate_single_caption(text):
    prompt = f"A comic about {text}."

    response = model(prompt)

    return response
    
    

# Function to Interpret Text with GPT-3 (Now Simplified)
def interpret_text_with_gpt(text):
    caption = generate_single_caption(text)
    refined_prompt = f"Entire page of comic panels, using clear embedded text for dialogue if applicable, for: {text}"
    return refined_prompt, caption

# Gradio Interface Function
def gradio_interface(state=None, text=None, selected_panel_index=None):
    global accumulated_story, favorite_panels
    
    if state is None:
        state = {}
        
    if "stage" not in state:
        state["stage"] = 1
    
    if state["stage"] == 1:
        if text is None:
            return state, "Please enter a story to begin.", accumulated_story, favorite_panels
        
        refined_prompt, caption = interpret_text_with_gpt(text)
        comic_panel_urls = generate_images_with_dalle(caption)
        
        html_output = ""
        for url in comic_panel_urls:
            html_output += f'<img src="{url}" alt="{caption}" width="300"/><br>{caption}<br>'
        
        state["stage"] = 2
        accumulated_story += f"{refined_prompt} "
        return state, html_output, accumulated_story, favorite_panels

    elif state["stage"] == 2:
        if selected_panel_index is not None and selected_panel_index in ["Panel 1", "Panel 2", "Panel 3", "Panel 4"]:
            selected_panel_index = ["Panel 1", "Panel 2", "Panel 3", "Panel 4"].index(selected_panel_index)
            favorite_panels.append(comic_panel_urls[selected_panel_index])
            state["stage"] = 1
        return state, "Ready for the next story input. You can now enter a new prompt.", accumulated_story, favorite_panels

if __name__ == "__main__":
    iface = gr.Interface(
        fn=gradio_interface,
        inputs=[
            "state",
            gr.inputs.Textbox(default="Type your story concept here"),
            gr.inputs.Radio(
                choices=["Panel 1", "Panel 2", "Panel 3", "Panel 4"],
                label="Favorite Panel",
                type="value",
                default=None,
                optional=True
            )
        ],
        outputs=[
            "state",
            gr.outputs.HTML(),
            "text",
            gr.outputs.Textbox(label="Favorite Panels")
        ]
    )
    iface.launch()
