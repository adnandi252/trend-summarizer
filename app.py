import os
import sys
import nltk

import spaces

@spaces.GPU
def dummy_gpu_task():
    return "Bypass ZeroGPU detection"

# Pre-download NLTK requirements on startup
print("Downloading NLTK requirements...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
print("NLTK download complete.")

# Add current directory to path to allow root imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from dashboard_app.main import app

if __name__ == "__main__":
    # Hugging Face Spaces exposes port 7860 by default
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
