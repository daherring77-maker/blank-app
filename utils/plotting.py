import streamlit as st
import plotly.graph_objects as go
import subprocess
import os

def plotly_config():
    """Standard config for clean, dark-friendly, minimal UI."""
    return {
        "displayModeBar": False,
        "scrollZoom": True,
        "staticPlot": False
    }

def apply_plotly_template(fig):
    """Enforce dark theme + clean layout."""
    fig.update_layout(
        template="plotly_dark",
        font=dict(size=14),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(font_size=13)
    )
    return fig

def add_download_buttons(data_dict, filename_base="data"):
    """Add CSV/JSON download for computed data."""
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download CSV",
            data="\n".join([f"{k},{v}" for k, v in data_dict.items() if isinstance(v, (int, float))]),
            file_name=f"{filename_base}_params.csv",
            mime="text/csv"
        )
    with col2:
        import json
        st.download_button(
            "📥 Download JSON",
            data=json.dumps(data_dict, indent=2),
            file_name=f"{filename_base}_config.json",
            mime="application/json"
        )


def run_ollama_command(prompt: str, model: str = "qwen3:8b") -> str:
    """Fast, synchronous Ollama call — returns final output only. No spinner delay."""
    try:
        # Use smaller, faster model by default (qwen3:8b ~2GB VRAM; ideal for RTX 4060)
        # Skip progress/status lines and decode safely
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=False,  # ← decode manually to avoid None/stdout issues
            timeout=120,  # tighter timeout — 2 mins max
            env={**os.environ, "NO_COLOR": "1", "OLLAMA_DEBUG": "0"}
        )

        # Safely decode stdout/stderr
        stdout = result.stdout.decode('utf-8', errors='ignore').strip() if result.stdout else ""
        stderr = result.stderr.decode('utf-8', errors='ignore').strip() if result.stderr else ""

        if result.returncode == 0:
            # Remove common non-response lines (Ollama's chatter)
            clean_lines = [
                line for line in stdout.splitlines()
                if not line.startswith((">>>", "Sending", "Loading", "time=", "Generating"))
            ]
            response = "\n".join(clean_lines).strip()
            return response if response else "✅ OK (no output)"
        else:
            return f"❌ Error {result.returncode}: {stderr or 'unknown'}"

    except subprocess.TimeoutExpired:
        return "⏱️ Timeout — try a shorter question or smaller model (e.g., `phi3`)."
    except FileNotFoundError:
        return "⚠️ Ollama not found — check `ollama --version` in terminal."
    except Exception as e:
        return f"💥 {type(e).__name__}: {e}"     
    
import json

def run_ollama_stream(prompt: str, model: str = "qwen3:8b"):
    """Yields tokens as they arrive — ideal for st.chat_message + st.write_stream"""
    try:
        proc = subprocess.Popen(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            env={**os.environ, "NO_COLOR": "1"}
        )
        
        while True:
            output = proc.stdout.readline()
            if not output and proc.poll() is not None:
                break
            if output:
                decoded = output.decode('utf-8', errors='replace').strip()
                # Skip status lines
                if not decoded.startswith((">>>", "Loading")):
                    yield decoded + "\n"
        
        stderr = proc.stderr.read().decode('utf-8', errors='replace')
        if proc.returncode != 0 and stderr.strip():
            yield f"\n❌ Error: {stderr.strip()}"
    except Exception as e:
        yield f"💥 Error: {e}"    