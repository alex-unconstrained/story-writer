import streamlit as st
from openai import OpenAI
import os
import uuid
import time
import pandas as pd
import io
import streamlit_book as stb

client = OpenAI()

# Load your OpenAI API key from an environment variable for security
#client.api_key = st.secrets["OPENAI_API_KEY"]
client.api_key = os.environ.get("OPENAI_API_KEY")

def display_dynamic_page(story_text, image_url):
    # Display the story text
    st.markdown(story_text)
    # Display the image using the URL
    st.image(image_url)



def generate_story(genre, level):
    try:
        prompt = f"Write a {genre} story suitable for a {level} reading level."
        print("Sending prompt...")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Ensure the response is extracted as a string
        story_text = completion.choices[0].message["content"] if completion.choices else ""
        print(story_text)
        return story_text
    except Exception as e:
        error_message = f"Error in generate_story: {e}"
        st.error(error_message)
        print(error_message)

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
        error_message = f"Error in generate_image: {e}"
        st.error(error_message)
        print(error_message)

def write_story_to_files(story_text, genre):
    story_pages = story_text.split("\n\n")  # Assuming each paragraph is a new page
    chapter_paths = []
    print("Writing story to files...")
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
    st.title('Dynamic Story and Image Generator')

    genre = st.radio("Choose a Genre", ('Fantasy', 'Sci-Fi', 'Mystery'))
    level_description = {
        'A': 'Beginner (Ages 5-7)',
        'B': 'Intermediate (Ages 8-10)',
        'C': 'Advanced (Ages 11+)'
    }
    level = st.selectbox("Select a Reading Level", options=level_description.keys(),
                         format_func=lambda x: f"{x} - {level_description[x]}")

    if genre and level:
        if st.button('Generate Story'):
            with st.spinner('Generating your story...'):
                story_text = generate_story(genre, level)
                if story_text:
                    story_pages = story_text.split("\n\n")  # Splitting story into pages
                    chapters = []
                    for page_text in story_pages:
                        image_url = generate_image(f"A scene depicting {page_text[:30]}...")
                        chapter_content = f"![Image]({image_url})\n\n{page_text}"
                        chapters.append(chapter_content)

                    # Configure Streamlit Book
                    stb.set_book_config(menu_title="Story Chapters", 
                                        show_page_number=True,
                                        show_scroll_top=True,
                                        wide_mode=True)
                    
                    # Add chapters to the book
                    for chapter in chapters:
                        stb.add_chapter(content=chapter)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()