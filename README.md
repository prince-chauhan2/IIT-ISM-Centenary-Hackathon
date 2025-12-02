
# The Code of Legacy: GenAI Video Pipeline
### IIT (ISM) Centenary Hackathon Submission

## 1. Project Overview
This project programmatically generates a documentary video showcasing the 100-year journey of IIT (ISM) Dhanbad ("From Black Gold to IIT"). 
Instead of manual editing, we built a **Python-based Generative AI Pipeline** that filters raw data, writes a script, generates multimodal assets, and renders the final video automatically.

## 2. Computational Mandate & Algorithms

### Phase 1: Data Filtering (Deep Search Algorithm)
* **Script:** `data_loader.py`
* **Logic:** We implemented a recursive file crawler that scans the `GenAI-FD-Dataset-2025`.
* **Technique:** It parses HTML (via `BeautifulSoup`) and PDF documents (via `pypdf`) looking for semantic keywords (*"History", "1926", "Centenary"*). It extracts specific dates from folder structures to build a chronological event timeline.

### Phase 2: GenAI Feature Engineering (Theme Injection)
* **Script:** `gen_script.py`
* **Model:** Google Gemini (via API)
* **Algorithm:** We used **Prompt Engineering** with a specific "Theme Transition" logic.
    * *Constraint:* Start with "Coal/Black" aesthetic (1926).
    * *Constraint:* End with "Fire/Red" aesthetic (2026).
    * The LLM structured the raw filtered data into a JSON timeline containing narration text and visual generation prompts.

### Phase 3: Asset Generation (Local Inference Pipeline)
* **Script:** `gen_assets_cuda.py`
* **Audio:** Used `Edge-TTS` (Microsoft Neural Voices) to generate human-quality voiceovers.
* **Visuals:** Used **Stable Diffusion v1.5** running locally via `diffusers` and `torch`.
    * *Method:* Local Inference (Offline Generation) to ensure data privacy and bypass API rate limits.
    * *Dynamic Prompting:* The code automatically injected style modifiers (*"Vintage 1926", "Cinematic Red Lighting"*) into the prompts before generation.

### Phase 4: Automated Assembly
* **Script:** `editor.py`
* **Tool:** `MoviePy`
* **Logic:** A programmatic editor that:
    1.  Loads the generated Audio/Image pairs.
    2.  Synchronizes image duration exactly to the audio waveform length.
    3.  Applies cross-fade transitions.
    4.  Renders the final `.mp4` output using `libx264`.

## 3. Tools & Stack
* **Language:** Python 3.9+
* **Libraries:** `pandas`, `moviepy`, `google-generativeai`, `edge-tts`, `diffusers`, `torch`
* **AI Models:** Gemini (Logic), Stable Diffusion v1.5 (Vision), Edge Neural (Audio)
