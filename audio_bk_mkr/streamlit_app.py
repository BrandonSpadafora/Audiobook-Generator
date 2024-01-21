# Streamlit Audiobook Conversion Tool

# Import necessary libraries
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import requests
from openai import OpenAI
import os
from playsound import playsound
from elevenlabs import voices as elevenlabs_voices
from elevenlabs import generate as elevenlabs_generate
from elevenlabs import save as elevenlabs_save
from pydub import AudioSegment
import re
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Get your OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with your API key
client = OpenAI(api_key=openai_api_key)

# Function to process text with OpenAI's GPT
def process_text_with_openai(user_text):
    """
    Generates structured text using OpenAI's GPT-4 model.
    """

    # Call OpenAI's GPT API to parse text and return structured data
    # Structure: [('Character', 'Text', 'Character_Count'), ...]
    context = (
    "Please structure the following story text into a dialogue format, "
    "where each line starts with the character's name or 'Narrator' followed by a colon, "
    "then the dialogue or narration. For example: "
    "Narrator: It was a dark and stormy night. "
    "Detective: Does anyone see the missing weapon? "
    "Narrator: His question hung in the air, met with silence from the team."
    )

    # Send the prompt to ChatGPT to structure the story text
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": user_text}
        ],
        model="gpt-4",
        max_tokens=1000
    )
    chatgpt_response = chat_completion.choices[0].message.content
    
    return chatgpt_response




def convert_structured_text_to_df(structured_text):

    """
    Converts structured text into a pandas DataFrame.
    The structured text should have each dialogue/narration on a new line,
    starting with either the character's name or 'Narrator:'.
    """
    
    # Initialize an empty list to store the data
    data = []

    # Split the structured text by new lines
    lines = structured_text.strip().split('\n')

    # Process each line
    for line in lines:
        # Split the line into character and text
        if ": " in line:  # Check for the colon followed by a space
            character, text = line.split(": ", 1)
            character = character.strip()
            # Trim whitespace and additional quotes if present
            text = text.strip(" '\"")
            character = character.strip()

            # Append to the data list
            data.append({
                'Character': character,
                'Text': text,
                'Character_Count': len(text)
            })

    # Convert the list of data into a DataFrame
    return pd.DataFrame(data)



def openai_tts(text, voice, output_path):
    try:
        client = OpenAIClient(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.audio.speech.create(
            model="tts-1-hd",
            speed=1,
            voice=voice,
            input=text,
        )
        response.stream_to_file(output_path)
        playsound(output_path)
        return True  # Indicating success
    except Exception as e:
        print(f"Error in openai_tts: {e}")
        return False  # Indicating failure


def elevenlabs_tts(text, voice, output_path):
    try:
        from elevenlabs import generate, save
        api_key = os.getenv('ELEVENLABS_API_KEY')
        audio_bytes = generate(
            text=text,
            api_key=api_key,
            voice=voice,
            model="eleven_monolingual_v1",
            output_format="mp3_44100_128"
        )
        save(audio=audio_bytes, filename=output_path)
        return True  # Indicating success
    except Exception as e:
        print(f"Error in elevenlabs_tts: {e}")
        return False  # Indicating failure

# Main function to choose the API and generate TTS MP3 file
def generate_tts_mp3(text, voice, api_choice):
    # Generate a unique file name with an absolute path
    current_directory = os.getcwd()  # Get the current working directory
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    audio_file_name = f"{voice}_{api_choice}_{timestamp}.mp3"
    audio_path = os.path.join(current_directory, audio_file_name)


    if api_choice == 'OpenAI':
        # Generate the audio file using OpenAI's TTS
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.audio.speech.create(model="tts-1-hd", speed=1, voice=voice, input=text)
        response.stream_to_file(audio_path)
    elif api_choice == 'ElevenLabs':
        # Generate the audio file using ElevenLabs' TTS
        audio_bytes = elevenlabs_generate(
            text=text,
            api_key=os.getenv('ELEVENLABS_API_KEY'),  # Ensure this environment variable is set
            voice=voice,
            model="eleven_monolingual_v1",
            output_format="mp3_44100_128"
        )
        elevenlabs_save(audio=audio_bytes, filename=audio_path)
    else:
        raise ValueError("Invalid API choice")

    # Check if the file exists
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    return audio_path


# Function to get ElevenLabs voices
def get_elevenlabs_voices():
    voices_list = elevenlabs_voices()
    return pd.DataFrame([{"Voice ID": voice.voice_id, "Name": voice.name} for voice in voices_list])

def concatenate_audios(audio_file_paths):
    combined = AudioSegment.empty()
    for file_path in audio_file_paths:
        # Ensure file_path is an absolute path
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        audio = AudioSegment.from_file(file_path)
        combined += audio
    return combined

# Main Streamlit app
def main():
    st.title("Audiobook Generator")

    # Step 1: Text input
    story_text = st.text_area("Enter your story here:")

    # Process Text Button
    if st.button("Process Text"):
        structured_text = process_text_with_openai(story_text)
        structured_data_df = convert_structured_text_to_df(structured_text)  # Convert structured text to DataFrame
        st.session_state.structured_data = structured_data_df
        st.dataframe(structured_data_df)


    # Voice and API selection for each character
    if 'structured_data' in st.session_state:
        characters = st.session_state['structured_data']['Character'].unique()
        api_selections = {}
        voice_selections = {}
        
        for character in characters:
            api_choice = st.radio(f"Select TTS API for {character}:", ["OpenAI", "ElevenLabs"], key=f"api_{character}")
            api_selections[character] = api_choice
            if api_choice == "OpenAI":
                voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            else:
                voice_df = get_elevenlabs_voices()  # This function needs to be defined
                voice_options = voice_df["Name"].tolist()
            selected_voice = st.selectbox(f"Select voice for {character}:", voice_options, key=f"voice_{character}")
            voice_selections[character] = selected_voice

        # Submit Voice Selections Button
        if st.button("Submit Voice Selections"):
            # Update the DataFrame with the API and Voice selections
            st.session_state['structured_data']['API'] = st.session_state['structured_data']['Character'].map(api_selections)
            st.session_state['structured_data']['Voice'] = st.session_state['structured_data']['Character'].map(voice_selections)
            
            # Generate audio files and concatenate them
            audio_file_paths = []
            for index, row in st.session_state['structured_data'].iterrows():
                audio_path = generate_tts_mp3(row.Text, row.Voice, row.API)  # Ensure this function is defined correctly
                st.write(f"Generated audio file: {audio_path}")  # Debugging print
                audio_file_paths.append(audio_path)

            print("All audio file paths:", audio_file_paths)  # Debugging print


            # Concatenate audio files into a single audiobook file
            audiobook = concatenate_audios(audio_file_paths)
            final_audiobook_path = "final_audiobook.mp3"
            audiobook.export(final_audiobook_path, format="mp3")

            # Provide a download link to the final audiobook file
            with open(final_audiobook_path, "rb") as file:
                st.download_button(
                    label="Download Audiobook",
                    data=file,
                    file_name=final_audiobook_path,
                    mime="audio/mp3"
                )
                    # Delete the individual audio files
            for file_path in audio_file_paths:
                try:
                    os.remove(file_path)
                    st.write(f"Deleted file: {file_path}")  # Optional: Confirm deletion in the app
                except OSError as e:
                    st.error(f"Error deleting file {file_path}: {e.strerror}")


# Run the Streamlit app
if __name__ == "__main__":
    main()



