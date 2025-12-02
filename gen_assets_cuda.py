import json
import os
import asyncio
import edge_tts
import torch
from diffusers import StableDiffusionPipeline

# --- CONFIGURATION ---
INPUT_FILE = "video_plan.json"
OUTPUT_DIR = "assets"
VOICE = "en-US-ChristopherNeural"

# --- LOCAL GPU SETUP ---
def load_local_model():
    print("⏳ Loading AI Model to GPU (This happens once)...")
    try:
        # We use v1-5 because it is fast and reliable
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.float16, 
            variant="fp16"
        )
        pipe = pipe.to("cuda")
        print("✅ Model loaded on NVIDIA GPU!")
        return pipe
    except Exception as e:
        print(f"❌ GPU Error: {e}")
        print("⚠️ Falling back to CPU (Slow but works)")
        pipe = StableDiffusionPipeline.from_pretrained(model_id)
        return pipe

# Initialize model globally
pipe = load_local_model()

async def generate_audio(text, filename):
    if os.path.exists(filename):
        print(f"   (Audio exists: {filename})")
        return
    print(f"🎙️ Generating Audio: {filename}...")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def generate_image(prompt, filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 1000:
        print(f"   (Image exists: {filename})")
        return

    print(f"🎨 Generating Image: {filename}...")
    # Add theme keywords
    final_prompt = f"{prompt}, (red theme:1.2), historical, cinematic lighting, 8k"
    
    # Generate on GPU (No Internet needed for this part)
    image = pipe(final_prompt).images[0]
    image.save(filename)
    print("   ✅ Image saved.")

async def main():
    if not os.path.exists(INPUT_FILE):
        print("❌ video_plan.json missing.")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    print(f"🚀 Starting Local Generation for {len(data['segments'])} segments...")

    for segment in data['segments']:
        seg_id = segment['id']
        audio_path = os.path.join(OUTPUT_DIR, f"audio_{seg_id}.mp3")
        image_path = os.path.join(OUTPUT_DIR, f"image_{seg_id}.jpg")

        # 1. Generate Audio
        await generate_audio(segment['narration'], audio_path)
        
        # 2. Generate Image (Locally)
        generate_image(segment['image_prompt'], image_path)

    print(f"\n🎉 Success! All files are in '{OUTPUT_DIR}'.")
    print("👉 Now run: python editor.py")

if __name__ == "__main__":
    asyncio.run(main())