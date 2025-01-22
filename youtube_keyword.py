import re
from youtube_transcript_api import YouTubeTranscriptApi

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
    raise ValueError("Could not extract video ID from the URL. Please check the URL and try again.")

def search_keyword_in_transcript(video_id, keyword):
    """Search for a keyword in the video transcript and return timestamps."""
    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Search for the keyword in the transcript
        matches = []
        for entry in transcript:
            if keyword.lower() in entry['text'].lower():
                matches.append((entry['start'], entry['text']))
        
        return matches
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def format_time(seconds):
    """Format time in seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"

def main():
    print("YouTube Keyword Timestamp Finder")
    video_url = input("Enter the YouTube video URL: ")
    keyword = input("Enter the keyword to search for: ")
    
    try:
        # Extract video ID
        video_id = extract_video_id(video_url)
        print(f"Video ID extracted: {video_id}")
        
        # Search for the keyword in the transcript
        results = search_keyword_in_transcript(video_id, keyword)
        
        if results:
            print(f"\nThe keyword '{keyword}' was found at the following times:\n")
            for start_time, text in results:
                formatted_time = format_time(start_time)
                print(f"- {formatted_time}: {text}")
        else:
            print(f"\nThe keyword '{keyword}' was not found in the transcript.")
    except ValueError as ve:
        print(ve)

if __name__ == "__main__":
    main()
