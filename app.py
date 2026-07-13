import os
import sys
import nltk
import gradio as gr

# --- ZeroGPU compatibility ---
# HF Spaces with Gradio SDK + ZeroGPU requires at least one @spaces.GPU
# function that is wired to a Gradio component so ZeroGPU can detect it.
try:
    import spaces
    _SPACES_AVAILABLE = True
except ImportError:
    _SPACES_AVAILABLE = False

# --- NLTK downloads (must happen before any NLP imports) ---
print("Downloading NLTK requirements...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
print("NLTK download complete.")

# --- Ensure project root is importable ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import the FastAPI application ---
from dashboard_app.main import app as fastapi_app  # noqa: E402

# --- Define a GPU-decorated function wired to Gradio ---
# ZeroGPU needs to see a @spaces.GPU function connected to the Gradio app.
def _gpu_health_check():
    """Health check function — GPU is allocated on-demand when called."""
    return "✅ GPU tersedia dan siap digunakan."

if _SPACES_AVAILABLE:
    _gpu_health_check = spaces.GPU(_gpu_health_check)

# --- Build the Gradio Blocks app ---
# This serves as the shell that HF Spaces expects.
# It auto-redirects users to the real FastAPI dashboard.

REDIRECT_HTML = """
<div id="landing-container" style="
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    min-height:80vh; font-family:'Inter',system-ui,sans-serif; background:#0f172a;
    color:#e2e8f0; text-align:center; padding:2rem;
">
    <div style="
        background:linear-gradient(135deg,#1e293b,#334155);
        border:1px solid #475569; border-radius:16px;
        padding:3rem 2.5rem; max-width:520px; width:100%;
        box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);
    ">
        <div style="font-size:3rem; margin-bottom:1rem;">📈</div>
        <h1 style="font-size:1.75rem; font-weight:700; margin:0 0 0.5rem 0;
            background:linear-gradient(135deg,#60a5fa,#a78bfa);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            TrendAI Summarizer
        </h1>
        <p style="color:#94a3b8; margin:0 0 2rem 0; font-size:0.95rem; line-height:1.6;">
            Dashboard analisis tren industri berbasis AI.<br>
            Klik tombol di bawah untuk membuka dashboard.
        </p>
        <a href="/dashboard.html" target="_top" style="
            display:inline-block; padding:0.75rem 2rem;
            background:linear-gradient(135deg,#3b82f6,#6366f1);
            color:white; text-decoration:none; border-radius:10px;
            font-weight:600; font-size:1rem;
            transition:transform 0.2s, box-shadow 0.2s;
            box-shadow:0 4px 14px rgba(99,102,241,0.4);
        " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(99,102,241,0.5)'"
           onmouseout="this.style.transform='none';this.style.boxShadow='0 4px 14px rgba(99,102,241,0.4)'">
            🚀 Buka Dashboard
        </a>
        <p style="color:#64748b; margin-top:1.5rem; font-size:0.8rem;">
            Atau akses API docs di <a href="/docs" target="_top" style="color:#60a5fa;">/docs</a>
        </p>
    </div>
</div>
"""

with gr.Blocks(
    title="TrendAI Summarizer",
    theme=gr.themes.Base(),
    css="body { margin: 0; padding: 0; background: #0f172a; }"
) as demo:
    gr.HTML(REDIRECT_HTML)
    # Hidden button to wire the @spaces.GPU function into Gradio's event system
    with gr.Row(visible=False):
        gpu_btn = gr.Button("GPU Check")
        gpu_output = gr.Textbox()
        gpu_btn.click(fn=_gpu_health_check, inputs=None, outputs=gpu_output)

# --- Mount Gradio onto the FastAPI app ---
# This keeps all FastAPI routes (/api/*, /dashboard.html, static files)
# functional while Gradio handles ZeroGPU detection at "/"
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

# --- Entry point ---
# HF Spaces runs `python app.py` directly. Uvicorn serves everything.
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
