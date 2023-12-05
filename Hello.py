import streamlit as st
from openai import OpenAI
import uuid
import time
import pandas as pd
import io
import streamlit_book as stb

client = OpenAI()

# Load your OpenAI API key from an environment variable for security
client.api_key = st.secrets["OPENAI_API_KEY"]

def generate_story(genre, level):
    try:
        prompt = f"Write a {genre} story suitable for a {level} reading level, with keywords in **bold** for learning."
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message
    except Exception as e:
        st.error("An error occurred while generating the story. Please try again.")
        print(e)

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        st.error("An error occurred while generating the image. Please try again.")
        print(e)

def main():
    st.title('Story and Image Generator')

    genre = st.radio("Choose a Genre", ('Fantasy', 'Sci-Fi', 'Mystery'))

    level_description = {
        'A': 'Beginner (Ages 5-7)',
        'B': 'Intermediate (Ages 8-10)',
        'C': 'Advanced (Ages 11+)'
    }
    level = st.selectbox("Select a Reading Level", options=level_description.keys(),
                         format_func=lambda x: f"{x} - {level_description[x]}")

    if genre and level:
        if st.button('Write'):
            with st.spinner('Generating your story...'):
                story_text = generate_story(genre, level)
                if story_text:
                    story_pages = story_text.split("\n\n")  # Assuming each paragraph is a new page
                    images = [generate_image(f"A scene depicting {line}") for line in story_pages]
                    stb.multiselect_page(story_pages, images)

# Responsive design considerations
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()