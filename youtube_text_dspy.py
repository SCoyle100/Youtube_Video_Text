import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import dspy  # Assuming DSPy is installed and properly set up

# Configure DSPy with your OpenAI API key
dspy.configure(lm=dspy.LM('openai/gpt-4o'))

# DSPy Module for Extracting Information
class ExtractInfo(dspy.Signature):
    """Extract structured information from text."""
    text: str = dspy.InputField()
    title: str = dspy.OutputField()
    headings: list[str] = dspy.OutputField()
    entities: list[dict[str, str]] = dspy.OutputField(desc="a list of entities and their metadata")

module = dspy.Predict(ExtractInfo)

def extract_video_id(url):
    """Extract video ID from a YouTube URL."""
    patterns = [
        r"(?<=v=)[^&#]+",
        r"(?<=be/)[^&#]+",
        r"(?<=/embed/)[^&#]+",
        r"(?<=/v/)[^&#]+"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(0)
    raise ValueError("Could not extract video ID from URL")

def fetch_video_title(video_id):
    """Fetch the video title using an HTTP request."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    if response.status_code == 200:
        title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
        if title_match:
            return title_match.group(1).replace(" - YouTube", "").strip()
    raise ValueError("Could not fetch video title.")

# Main Script
video_url = input("Enter the full YouTube URL: ")
video_id = extract_video_id(video_url)

# Fetch YouTube video title without using pytube
video_title = fetch_video_title(video_id)

# Get transcript of the video
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# Format transcript using TextFormatter from youtube_transcript_api library
formatter = TextFormatter()
transcript_text = formatter.format_transcript(transcript)

# Save transcript text to a file named after the video title
safe_title = "".join([c if c.isalnum() or c.isspace() else "_" for c in video_title])  # Remove unsafe characters
filename = f"{safe_title}_text.txt"

with open(filename, 'w', encoding='utf-8') as f:
    f.write(transcript_text)

print(f"Transcript saved to {filename}")

# Send transcript text to the DSPy module for extracting information
response = module(text=transcript_text)

# Print extracted information
print("\n--- Extracted Information ---")
print(f"Title: {response.title}")
print(f"Headings: {response.headings}")
print(f"Entities: {response.entities}")

# Optionally, save the extracted information to a file
info_filename = f"{safe_title}_info.txt"
with open(info_filename, 'w', encoding='utf-8') as f:
    f.write(f"Title: {response.title}\n")
    f.write(f"Headings: {', '.join(response.headings)}\n")
    f.write("Entities:\n")
    for entity in response.entities:
        f.write(f"  - {entity}\n")

print(f"Extracted information saved to {info_filename}")
