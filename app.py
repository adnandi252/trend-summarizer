import os
import sys
import nltk
import gradio as gr

# --- Configuration ---
PORT = int(os.environ.get("PORT", 7860))
IS_HF_SPACE = bool(os.environ.get("SPACE_ID"))

# --- ZeroGPU compatibility ---
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

# --- GPU-decorated function wired to Gradio ---
def _gpu_health_check():
    """Health check — GPU is allocated on-demand when called."""
    return "✅ GPU tersedia dan siap digunakan."

if _SPACES_AVAILABLE:
    _gpu_health_check = spaces.GPU(_gpu_health_check)

# --- Gradio Blocks interface ---
# Serves as the "shell" that HF Spaces expects.
# Auto-redirects users to the real FastAPI dashboard.

REDIRECT_HTML = """
<div style="
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
<script>
    // Auto-redirect to dashboard after 2 seconds
    setTimeout(function() {
        window.top.location.href = '/dashboard.html';
    }, 2000);
</script>
"""

with gr.Blocks(
    title="TrendAI Summarizer",
    theme=gr.themes.Base(),
    css="body { margin: 0; padding: 0; background: #0f172a; }"
) as demo:
    gr.HTML(REDIRECT_HTML)
    # Hidden button to wire @spaces.GPU into Gradio's event system
    with gr.Row(visible=False):
        gpu_btn = gr.Button("GPU Check")
        gpu_output = gr.Textbox()
        gpu_btn.click(fn=_gpu_health_check, inputs=None, outputs=gpu_output)

# --- Server startup ---
if __name__ == "__main__":
    print(f"Starting server on port {PORT}...")

    # Launch Gradio server (handles port binding — only ONE server)
    # prevent_thread_lock=True so we can configure routes after
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        prevent_thread_lock=True,
        share=False,
    )

    # Mount FastAPI at a hidden path solely for lifespan event propagation.
    # This ensures @app.on_event("startup") handlers in main.py fire
    # (project reset, weekly scheduler, etc.)
    demo.app.mount("/_internal", fastapi_app)

    # Insert all FastAPI routes at the BEGINNING of Gradio's route list.
    # Gradio has a catch-all route (/{path:path}) that intercepts every
    # request. By inserting our routes first, paths like /dashboard.html,
    # /api/*, /static/*, / are matched BEFORE Gradio's catch-all.
    for route in reversed(list(fastapi_app.routes)):
        demo.app.routes.insert(0, route)

    print("✅ FastAPI routes injected into Gradio server. Dashboard is ready.")

    # Keep the main thread alive (Gradio server runs in background thread)
    import threading
    threading.Event().wait()

