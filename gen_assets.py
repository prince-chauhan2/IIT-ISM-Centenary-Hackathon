import json
import os
import requests
import asyncio
import edge_tts
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

INPUT_FILE = "video_plan.json"
OUTPUT_DIR = "assets"

# *** NEW URL (Router) ***
HF_API_URL = "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
VOICE = "en-US-ChristopherNeural"

async def generate_audio(text, filename):
    print(f"🎙️ Generating Audio: {filename}...")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def generate_image(prompt, filename):
    print(f"🎨 Generating Image: {filename}...")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Retry logic
    for i in range(3):
        try:
            response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print("   ✅ Image saved.")
                return True
            else:
                print(f"   ⚠️ API Error: {response.text}")
                import time
                time.sleep(5)
        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
    return False

async def main():
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: video_plan.json not found.")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    tasks = []
    for segment in data['segments']:
        seg_id = segment['id']
        narration = segment['narration']
        image_prompt = segment['image_prompt']

        audio_path = os.path.join(OUTPUT_DIR, f"audio_{seg_id}.mp3")
        image_path = os.path.join(OUTPUT_DIR, f"image_{seg_id}.jpg")

        # Create audio immediately
        await generate_audio(narration, audio_path)
        
        # Generate image (Sync because requests isn't async)
        # Add "Red" theme enforcement to prompt
        final_prompt = f"{image_prompt}, (red theme:1.3), historical, 8k resolution, cinematic lighting"
        generate_image(final_prompt, image_path)

    print(f"🎉 Success! All assets saved in '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    asyncio.run(main())