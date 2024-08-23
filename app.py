import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import re

load_dotenv()  # Load all the environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points in 250 words. Please provide the summary of the text given here: """


# Function to get the transcript from a YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        
        # Fetch transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine transcript into a single string
        transcript = " ".join([entry["text"] for entry in transcript_data])
        return transcript

    except NoTranscriptFound:
        return "No transcript available for this video."
    except Exception as e:
        return str(e)


# Function to extract video ID from various YouTube URL formats
def extract_video_id(url):
    video_id = None
    # Regular expression to handle different YouTube URL formats
    patterns = [
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)",  # Matches standard and short URLs
        r"youtube\.com/embed/([^&\n?#]+)",  # Matches embedded URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    return video_id


# Function to get summary using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    else:
        st.error("Invalid YouTube URL")

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if "No transcript available" in transcript_text:
        st.error(transcript_text)
    else:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
