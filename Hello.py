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
        prompt = f"Write a {genre} story suitable for a {level} reading level."
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

def write_story_to_files(story_text, genre):
    story_pages = story_text.split("\n\n")  # Assuming each paragraph is a new page
    chapter_paths = []
    for i, page_text in enumerate(story_pages, start=1):
        chapter_dir = f"pages/{i:02d}_chapter_{genre}"
        os.makedirs(chapter_dir, exist_ok=True)
        
        # Write text
        with open(f"{chapter_dir}/page.md", "w") as file:
            file.write(page_text)
        
        # Generate image URL
        image_url = generate_image(f"A scene depicting {page_text[:30]}...")
        if image_url:
            with open(f"{chapter_dir}/image_url.txt", "w") as file:
                file.write(image_url)

        chapter_paths.append(chapter_dir)
    return chapter_paths

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
                    chapter_paths = write_story_to_files(story_text, genre)
                    for path in chapter_paths:
                        with open(f"{path}/page.md", "r") as file:
                            page_text = file.read()
                        with open(f"{path}/image_url.txt", "r") as file:
                            image_url = file.read().strip()
                        st.markdown(page_text)
                        st.image(image_url)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()