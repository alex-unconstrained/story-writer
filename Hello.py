import streamlit as st
import openai
import uuid
import time
import pandas as pd
import io


# Load your OpenAI API key from an environment variable for security
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_story(genre, level):
    try:
        # Formulate the prompt
        prompt = f"Write a {genre} story suitable for a {level} reading level."
        # Call the OpenAI API
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=500)
        return response.choices[0].text
    except Exception as e:
        # Handle exceptions like API errors
        st.error("An error occurred while generating the story. Please try again.")
        print(e)

def main():
    st.title('Story Generator')

    # Genre Selection with enhanced UI
    genre = st.radio("Choose a Genre", ('Fantasy', 'Sci-Fi', 'Mystery'))

    # Reading Level Selection with additional information
    level_description = {
        'A': 'Beginner (Ages 5-7)',
        'B': 'Intermediate (Ages 8-10)',
        'C': 'Advanced (Ages 11+)'
    }
    level = st.selectbox("Select a Reading Level", options=level_description.keys(),
                         format_func=lambda x: f"{x} - {level_description[x]}")

    # Write Button with conditional activation
    if genre and level:
        if st.button('Write'):
            with st.spinner('Generating your story...'):
                story = generate_story(genre, level)
                if story:
                    st.text_area("Your Story", story, height=300)

# Responsive design considerations
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
