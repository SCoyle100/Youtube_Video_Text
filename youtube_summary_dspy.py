import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import dspy  # Assuming DSPy is installed and properly set up


dspy.configure(lm=dspy.LM('openai/gpt-4o'))

# DSPy Chain of Thought Module
class Outline(dspy.Signature):
    """Outline a thorough overview of a topic."""
    topic: str = dspy.InputField()
    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(desc="mapping from section headings to subheadings")

class DraftSection(dspy.Signature):
    """Draft a top-level section of an article."""
    topic: str = dspy.InputField()
    section_heading: str = dspy.InputField()
    section_subheadings: list[str] = dspy.InputField()
    content: str = dspy.OutputField(desc="markdown-formatted section")

class DraftArticle(dspy.Module):
    def __init__(self):
        self.build_outline = dspy.ChainOfThought(Outline)
        self.draft_section = dspy.ChainOfThought(DraftSection)

    def forward(self, topic, transcript_text):
        outline = self.build_outline(topic=topic)
        sections = []
        for heading, subheadings in outline.section_subheadings.items():
            section = self.draft_section(topic=topic, section_heading=heading, section_subheadings=subheadings)
            sections.append(section.content)
        return dspy.Prediction(title=outline.title, sections=sections)

draft_article = DraftArticle()

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

# Generate a smart summary using the Chain of Thought module
response = draft_article.forward(topic=video_title, transcript_text=transcript_text)

# Print the generated summary
print("\n--- Generated Smart Summary ---")
print(f"Title: {response.title}")
for section in response.sections:
    print(section)

# Save the summary to a file
summary_filename = f"{safe_title}_summary.txt"
with open(summary_filename, 'w', encoding='utf-8') as f:
    f.write(f"Title: {response.title}\n")
    for section in response.sections:
        f.write(f"{section}\n\n")

print(f"Smart summary saved to {summary_filename}")
