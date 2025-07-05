import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

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

# Provide the full YouTube URL
video_url = input("Enter the full YouTube URL: ")
video_id = extract_video_id(video_url)

# Fetch YouTube video title without using pytube
video_title = fetch_video_title(video_id)

# Get transcript of the video
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# Format transcript using TextFormatter from youtube_transcript_api library
formatter = TextFormatter()
transcript_text = "\n".join(item['text'] for item in transcript)   # formatter.format_transcript(transcript)

# Write transcript text to a text file named after the video title
safe_title = "".join([c if c.isalnum() or c.isspace() else "_" for c in video_title])  # Remove unsafe characters
filename = f"{safe_title}_text.txt"

with open(filename, 'w', encoding='utf-8') as f:
    f.write(transcript_text)

print(f"Transcript saved to {filename}")
