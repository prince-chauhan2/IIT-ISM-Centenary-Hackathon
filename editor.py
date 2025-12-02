import json
import os
import sys

# Try importing MoviePy
try:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
    except ImportError:
        print("❌ Error: MoviePy is not installed. Run: pip install \"moviepy<2.0\"")
        sys.exit(1)

# --- CONFIGURATION ---
INPUT_FILE = "video_plan.json"
ASSETS_DIR = "assets"
OUTPUT_VIDEO = "final_submission.mp4"

def create_video():
    if not os.path.exists(ASSETS_DIR):
        print("Error: Assets folder not found. You must run gen_assets.py first.")
        return

    # 1. Load the Script Plan
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    clips = []
    
    print(" assembling video segments...")

    # 2. Loop through every segment to create clips
    for segment in data['segments']:
        seg_id = segment['id']
        
        # Define file paths
        audio_path = os.path.join(ASSETS_DIR, f"audio_{seg_id}.mp3")
        image_path = os.path.join(ASSETS_DIR, f"image_{seg_id}.jpg")

        # Check if files exist
        if not os.path.exists(audio_path) or not os.path.exists(image_path):
            print(f"Skipping Segment {seg_id}: Missing audio or image files.")
            continue

        # 3. Create the Clip
        # Load Audio
        audio_clip = AudioFileClip(audio_path)
        
        # Load Image and set it to last exactly as long as the audio
        video_clip = ImageClip(image_path).set_duration(audio_clip.duration)
        
        # Combine them
        video_clip = video_clip.set_audio(audio_clip)
        
        # Add to list
        clips.append(video_clip)

    if not clips:
        print("No clips were created. Check your assets folder.")
        return

    # 4. Concatenate (Stitch) all clips together
    final_video = concatenate_videoclips(clips, method="compose")

    # 5. Export final video
    print(f"Rendering final video to {OUTPUT_VIDEO}...")
    # fps=24 is standard for film/video
    final_video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac")
    print("Done! Video is ready.")

if __name__ == "__main__":
    create_video()