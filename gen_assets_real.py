import json
import os
import shutil
import asyncio
import edge_tts
import torch
from diffusers import StableDiffusionPipeline

# --- CONFIGURATION ---
INPUT_PLAN = "video_plan.json"
INPUT_ASSETS = "available_assets.json"
OUTPUT_DIR = "assets"
VOICE = "en-US-ChristopherNeural"

# --- 1. SETUP AI MODEL (Local GPU) ---
def load_model():
    print("⏳ Loading AI Model for Centenary generation...")
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", 
            torch_dtype=torch.float16, 
            variant="fp16"
        )
        pipe = pipe.to("cuda")
        print("✅ GPU Model Loaded! (Will be used for 2026/Missing photos)")
        return pipe
    except:
        print("⚠️ GPU Error. Falling back to CPU (Slower).")
        return StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")

# Initialize Model
pipe = load_model()

async def generate_audio(text, filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0: return
    print(f"🎙️ Generating Audio: {filename}...")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def generate_ai_image(prompt, filename, style="cinematic"):
    print(f"🎨 AI Generating: {filename} ({style})...")
    
    # Custom styling based on era
    if "red" in style or "fire" in style:
        final_prompt = f"{prompt}, (glowing red theme:1.4), fireworks, celebration, cinematic lighting, 8k, night time"
    elif "vintage" in style:
        final_prompt = f"{prompt}, sepia tone, 1926 vintage photograph, grainy, historical"
    else:
        final_prompt = f"{prompt}, photorealistic, 8k, highly detailed"

    image = pipe(final_prompt).images[0]
    image.save(filename)
    print("   ✅ AI Image saved.")

def get_real_image(target_year, assets, used_images):
    """Finds best unused real image for the year."""
    best_match = None
    min_diff = float('inf')

    for asset in assets:
        if asset['path'] in used_images: continue
        
        try:
            asset_year = int(asset['date'].split('-')[0])
            diff = abs(asset_year - target_year)
            
            # Only accept if it's somewhat close (within 10 years)
            if diff < min_diff and diff < 15:
                min_diff = diff
                best_match = asset
        except:
            continue

    return best_match

async def main():
    if not os.path.exists(INPUT_PLAN): return
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    with open(INPUT_PLAN, 'r') as f: plan = json.load(f)
    
    # Load Real Assets
    real_images = []
    if os.path.exists(INPUT_ASSETS):
        with open(INPUT_ASSETS, 'r') as f:
            real_images = [x for x in json.load(f) if x['type'] == 'image']

    used_images = set()

    print(f"🚀 Starting Hybrid Generation...")

    for i, segment in enumerate(plan['segments']):
        seg_id = segment['id']
        text = segment['narration'].lower()
        image_prompt = segment['image_prompt']
        
        # Audio
        await generate_audio(segment['narration'], os.path.join(OUTPUT_DIR, f"audio_{seg_id}.mp3"))
        
        dst_path = os.path.join(OUTPUT_DIR, f"image_{seg_id}.jpg")
        
        # --- DECISION LOGIC ---
        # 1. Is it the CENTENARY (2026)? -> FORCE AI (Red Theme)
        if "2026" in text or "centenary" in text or "celebration" in text or "future" in text:
            print(f"🔹 Segment {seg_id}: Future Event detected. Using AI (Red Theme).")
            generate_ai_image(image_prompt, dst_path, style="red fire celebration")
            continue

        # 2. Is it ANCIENT History (1926)? -> Try Real, fallback to AI (Vintage)
        target_year = 2016 # Default
        if "1926" in text: target_year = 1926
        elif "1957" in text: target_year = 1957
        elif "1976" in text: target_year = 1976
        elif "2016" in text: target_year = 2016

        match = get_real_image(target_year, real_images, used_images)
        
        if match:
            # Use Real Photo
            try:
                shutil.copy(match['path'], dst_path)
                used_images.add(match['path'])
                print(f"🔹 Segment {seg_id}: Used Real Photo ({match['date']})")
            except:
                generate_ai_image(image_prompt, dst_path, style="photorealistic")
        else:
            # No real photo found -> Fallback to AI
            style = "vintage" if target_year < 1980 else "photorealistic"
            print(f"🔹 Segment {seg_id}: No real photo for {target_year}. Using AI ({style}).")
            generate_ai_image(image_prompt, dst_path, style=style)

    print(f"🎉 Assets Ready! Run: python editor.py")

if __name__ == "__main__":
    asyncio.run(main())