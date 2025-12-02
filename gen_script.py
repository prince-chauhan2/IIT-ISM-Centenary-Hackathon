import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OUTPUT_FILE = "video_plan.json"

# List of all possible model names to try (in order of preference)
MODEL_CANDIDATES = [
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-1.0-pro",
    "gemini-1.0-pro-latest",
    "gemini-pro",
    "gemini-1.5-pro"
]

def create_prompt():
    return """
    You are a documentary director creating a script for: "The Centenary of IIT (ISM) Dhanbad".
    CRITICAL CONSTRAINT: The video must be exactly 2 minutes (approx 8 segments).
    
    THEME TRANSITION:
    - START (1926): Dark, Coal Black, Vintage Monochrome.
    - END (2026): Vibrant Red, Fire/Energy.
    
    MANDATORY TIMELINE:
    1. 1926: Founding, Lord Irwin, British Architecture (Black/White).
    2. 1957: Expansion to ISM.
    3. 1976: Golden Jubilee, Indira Gandhi.
    4. 2016: IIT Status.
    5. 2026: Centenary Celebration (Glowing Red).

    OUTPUT JSON FORMAT:
    {
        "segments": [
            {
                "id": 1,
                "narration": "In the land of black gold...",
                "image_prompt": "Vintage 1926 photograph, British colonial architecture, grainy black and white style"
            }
        ]
    }
    """

def main():
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    
    working_model = None

    print("🔍 Testing models to find one that works for you...")
    
    # LOOP to find a working model
    for model_name in MODEL_CANDIDATES:
        try:
            print(f"   Trying: {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            # Send a tiny test prompt
            model.generate_content("test")
            print("✅ WORKS!")
            working_model = model
            break
        except Exception as e:
            print("❌ Failed")
            print(e) # Uncomment to see exact error

    if not working_model:
        print("\n❌ CRITICAL: No working models found. Check your API Key or Region.")
        return

    print("\n🔥 Generating Script...")
    try:
        response = working_model.generate_content(create_prompt())
        content = response.text.replace("```json", "").replace("```", "").strip()
        
        # JSON Cleaning
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            content = content[start:end]

        script_json = json.loads(content)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(script_json, f, indent=4)
            
        print(f"🎉 SUCCESS! Script saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    main()