"""
Entry point for local development.
On HF Spaces (Docker SDK), the Dockerfile runs uvicorn directly.
"""
import os
import sys
import nltk

# Pre-download NLTK requirements
print("Downloading NLTK requirements...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
print("NLTK download complete.")

# Ensure project root is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_app.main import app  # noqa: E402, F401

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
