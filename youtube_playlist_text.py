import re
from pytube import Playlist, YouTube
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

def fetch_transcript(video_url):
    """Fetch transcript and title for a given video URL."""
    video_id = extract_video_id(video_url)
    yt = YouTube(video_url)
    video_title = yt.title
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"Error fetching transcript for '{video_title}'. Error: {str(e)}")
        return

    formatter = TextFormatter()
    transcript_text = formatter.format_transcript(transcript)

    safe_title = "".join([c if c.isalnum() or c.isspace() else "_" for c in video_title])  # Remove unsafe characters
    filename = f"{safe_title}_text.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(transcript_text)
    
    print(f"Saved transcript for '{video_title}' to {filename}")

# Input playlist URL
playlist_url = input("Enter the full YouTube playlist URL: ")

try:
    playlist = Playlist(playlist_url)
except Exception as e:
    print(f"Error fetching playlist. Error: {str(e)}")
    exit()

print(f"Found {len(playlist.video_urls)} videos in the playlist.")
for url in playlist.video_urls:
    print(url)    

# Loop through each video in the playlist
for video_url in playlist.video_urls:
    try:
        fetch_transcript(video_url)
    except Exception as e:
        print(f"Failed to fetch transcript for video at {video_url}. Error: {e}")

print("Finished processing the playlist!")

