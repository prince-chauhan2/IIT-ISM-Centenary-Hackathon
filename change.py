import os
import json
import re
from bs4 import BeautifulSoup
from pypdf import PdfReader

# --- CONFIGURATION ---
OUTPUT_DATA_FILE = "filtered_data.json"
OUTPUT_ASSETS_FILE = "available_assets.json"

# Broader keywords to ensure we catch everything
KEYWORDS = [
    "history", "established", "1926", "legacy", "campus", 
    "diamond jubilee", "centenary", "convocation", "ranking", 
    "president", "director", "opening", "coal", "mining", 
    "petroleum", "earth", "department", "alumni"
]

def extract_text_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return " ".join(soup.get_text().split())
    except:
        return ""

def extract_text_from_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        # Limit to first 3 pages to avoid freezing on huge docs
        for i, page in enumerate(reader.pages):
            if i > 2: break
            text += page.extract_text() or ""
        return " ".join(text.split())
    except:
        return ""

def extract_date_from_path(path):
    match = re.search(r'\d{4}-\d{2}-\d{2}', path)
    if match:
        return match.group(0)
    return "Unknown Date"

def main():
    relevant_data = []
    visual_assets = []
    
    print(f"🚀 Scanning deep inside: {os.getcwd()}")
    print("------------------------------------------------")
    
    # Walk through EVERY folder recursively
    for root, dirs, files in os.walk(os.getcwd()):
        
        # Skip system folders
        if ".git" in root or "_pycache_" in root:
            continue

        folder_date = extract_date_from_path(root)
        folder_name = os.path.basename(root)

        for file in files:
            file_path = os.path.join(root, file)
            
            # 1. HTML Analysis
            if file.endswith("index.html"):
                content = extract_text_from_html(file_path)
                if any(k in content.lower() for k in KEYWORDS):
                    relevant_data.append({
                        "type": "text_fact", "date": folder_date, 
                        "source": folder_name, "content": content[:500]
                    })
                    print(f"✅ Found Fact: {folder_name}")

            # 2. PDF Analysis
            elif file.endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
                if any(k in content.lower() for k in KEYWORDS):
                    relevant_data.append({
                        "type": "text_fact", "date": folder_date,
                        "source": folder_name, "content": content[:500]
                    })
                    print(f"📄 Found PDF Fact: {file}")

            # 3. Image Analysis (JPG/PNG)
            elif file.lower().endswith(('.jpg', '.jpeg', '.png', '.avif')):
                visual_assets.append({
                    "type": "image", "date": folder_date,
                    "filename": file, "path": file_path
                })

    print("------------------------------------------------")
    
    # Save Results
    if relevant_data:
        # Sort by date
        relevant_data.sort(key=lambda x: x['date'])
        with open(OUTPUT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(relevant_data, f, indent=4)
        print(f"🎉 Success! Saved {len(relevant_data)} facts to {OUTPUT_DATA_FILE}")
    else:
        print("❌ No text data found. Please check if 'news_articles' folder is present.")

    if visual_assets:
        visual_assets.sort(key=lambda x: x['date'])
        with open(OUTPUT_ASSETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(visual_assets, f, indent=4)
        print(f"📸 Indexed {len(visual_assets)} images to {OUTPUT_ASSETS_FILE}")

if _name_ == "_main_":
    main()
