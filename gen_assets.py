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

# Using Hugging Face Router for Stability AI (Images)
HF_API_URL = "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# TTS CONFIGURATION
# We use Microsoft Edge TTS (Free & High Quality)
# Voices: "en-US-ChristopherNeural" (Male), "en-US-AriaNeural" (Female)
VOICE = "en-US-ChristopherNeural"

async def generate_audio(text, filename):
    print(f"🎙️ Generating Audio: {filename}...")
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(filename)
        print(f"   ✅ Audio saved.")
    except Exception as e:
        print(f"   ❌ TTS Error: {e}")

def generate_image(prompt, filename):
    print(f"🎨 Generating Image: {filename}...")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Enforce Red/Coal Theme in every image
    styled_prompt = f"{prompt}, (red theme:1.2), (coal dust atmosphere:0.8), cinematic lighting, 8k resolution, photorealistic"
    
    # Retry logic (3 attempts)
    for i in range(3):
        try:
            response = requests.post(HF_API_URL, headers=headers, json={"inputs": styled_prompt})
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print("   ✅ Image saved.")
                return True
            else:
                print(f"   ⚠️ API Error (Attempt {i+1}): {response.text}")
                import time
                time.sleep(5)
        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
    return False

async def main():
    # 1. Check for the plan
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: video_plan.json not found. Run gen_script.py first.")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Load the Blueprint
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    print(f"🚀 Generating assets for {len(data['segments'])} segments...")

    # 3. Execution Loop
    for segment in data['segments']:
        seg_id = segment['id']
        narration = segment['narration']
        image_prompt = segment['image_prompt']

        # Define filenames
        audio_path = os.path.join(OUTPUT_DIR, f"audio_{seg_id}.mp3")
        image_path = os.path.join(OUTPUT_DIR, f"image_{seg_id}.jpg")

        # Generate Audio (Async)
        await generate_audio(narration, audio_path)
        
        # Generate Image (Sync)
        generate_image(image_prompt, image_path)

    print(f"🎉 Success! Check the '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    asyncio.run(main())