# Audiobook-Generator

## Description
This project is a Streamlit-based web application that converts my stories into an audiobook. It processes the text to identify different characters and narration, allows users to assign specific voices (using OpenAI and ElevenLabs TTS APIs), generates individual audio files for each piece of dialogue and narration, and then concatenates these into a single audiobook file.

## Warning
Creating audio files can take up a lot of storage space, and this is untested on very large stories with lots of characters. This also utilizes the Openai and elevenlabs APIs which cost money to use. 

## Why Did I Make This?
I was thinking that it'd be cool to turn the book I am currently in the process of writing into an audiobook.
After looking at different TTS software I felt like doing this all manually between multiple different tabs is a lot of work.
I would have to manually separate all the text and label it based on who is talking, then I'd have to find the voice I want to use,
then copy and paste each bit of dialogue and narration into the right website, then I'd have to organize all the audio files,
and finally, I'd have to combine everything in another piece of software like garageband or imovie or some other software that I'd either have to pay for and/or learn how to use. That's hours worth of work for one story. Instead, I decided to program this webapp so that I don't have to do all of that work. 

## Features
* Text processing to identify dialogue and narration.
* Integration with OpenAI and ElevenLabs TTS APIs for voice synthesis.
* Generation of individual audio files for dialogues and narration.
* Concatenation of individual audio files into a single audiobook.
* Splits the text in the rows if they go over the character limit of 3000 (this prevents the APIs from throwing errors because I know for a fact that the Openai API will throw an error and not generate text if you try to have it do ~4000 characters)

## Configuration
You need to set up API keys for OpenAI and ElevenLabs. These keys should be stored in a .env file at the root of the project with the following format:

OPENAI_API_KEY='your_openai_api_key_here'

ELEVENLABS_API_KEY='your_elevenlabs_api_key_here'






