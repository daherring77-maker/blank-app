import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.plotting import plotly_config, apply_plotly_template
from utils.plotting import run_ollama_command
import re

st.title("🌊 Parametric Surface Explorer")

# --- Mode ---
mode = st.radio("Mode", ["Explorer", "Lesson: Critical Points & Curvature"], 
                horizontal=True, label_visibility="collapsed")

if mode == "Lesson: Critical Points & Curvature":
    st.info("""
    🎯 **Goal**: Find saddle points, maxima, minima.
    💡 Try:
      - `z = x² - y²` → classic saddle  
      - `z = x² + y²` → paraboloid (minimum)  
      - `z = -x⁴ + y²` → monkey saddle?  
    📚 Look for where contour lines *cross* — that’s a saddle!
    """, icon="🔍")

# --- Function & Domain Controls ---
with st.expander("🎛️ Function & Domain", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        preset = st.selectbox("Preset function", [
            "sin(x)·cos(y)",
            "x² - y² (saddle)",
            "x² + y² (bowl)",
            "sin(x² + y²)",
            "exp(-x²-y²) (Gaussian)",
            "sin(x) + cos(y)",
            "x·y·exp(-x²-y²)",
            "Custom"
        ])
    with col2:
        if preset == "Custom":
            expr = st.text_input("f(x, y) = ", value="np.sin(x) * np.cos(y)", key="custom_expr")
        else:
            mapping = {
                "sin(x)·cos(y)": "np.sin(x) * np.cos(y)",
                "x² - y² (saddle)": "x**2 - y**2",
                "x² + y² (bowl)": "x**2 + y**2",
                "sin(x² + y²)": "np.sin(x**2 + y**2)",
                "exp(-x²-y²) (Gaussian)": "np.exp(-(x**2 + y**2))",
                "sin(x) + cos(y)": "np.sin(x) + np.cos(y)",
                "x·y·exp(-x²-y²)": "x * y * np.exp(-(x**2 + y**2))"
            }
            expr = mapping[preset]

        x_range = st.slider("X range", 0.5, 6.0, 3.0, step=0.5)
        y_range = st.slider("Y range", 0.5, 6.0, 3.0, step=0.5)

with st.expander("🎨 Visual Style", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        resolution = st.slider("Resolution", 20, 80, 40, step=5)
        colorscale = st.selectbox("Colorscale", ["Blues", "Viridis", "Turbo", "RdBu", "Ice"], index=0)
        show_surface = st.toggle("Surface", value=True)
        show_wire = st.toggle("Wireframe", value=True)
    with col2:
        opacity = st.slider("Opacity", 0.2, 1.0, 0.85, step=0.05)
        wire_step = st.slider("Wire step", 1, 10, 3, help="Larger = sparser wires")
        animate = st.toggle("🔄 Auto-rotate", value=False)

# --- Compute surface ---
@st.cache_data(ttl=300)
def compute_surface(expr, x_range, y_range, resolution):
    try:
        x = np.linspace(-x_range, x_range, resolution)
        y = np.linspace(-y_range, y_range, resolution)
        X, Y = np.meshgrid(x, y)
        # Safe eval — only allow numpy & basic ops
        allowed_names = {"np": np, "x": X, "y": Y, "sin": np.sin, "cos": np.cos, "exp": np.exp, "log": np.log}
        Z = eval(expr, {"__builtins__": {}}, allowed_names)
        return X, Y, Z
    except Exception as e:
        st.error(f"⚠️ Invalid expression: {e}")
        # Fallback
        X, Y = np.meshgrid(np.linspace(-3,3,20), np.linspace(-3,3,20))
        Z = np.sin(X) * np.cos(Y)
        return X, Y, Z

X, Y, Z = compute_surface(expr, x_range, y_range, resolution)

# --- Build figure ---
fig = go.Figure()

# Surface
if show_surface:
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=colorscale,
        opacity=opacity,
        showscale=False,
        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.3, roughness=0.4),
        lightposition=dict(x=100, y=200, z=150)
    ))

# Wireframe
if show_wire:
    # Efficient wireframe: only every `wire_step` line
    for i in range(0, X.shape[0], wire_step):
        fig.add_trace(go.Scatter3d(
            x=X[i, :], y=Y[i, :], z=Z[i, :],
            mode='lines',
            line=dict(color='white', width=1),
            showlegend=False
        ))
    for j in range(0, X.shape[1], wire_step):
        fig.add_trace(go.Scatter3d(
            x=X[:, j], y=Y[:, j], z=Z[:, j],
            mode='lines',
            line=dict(color='white', width=1),
            showlegend=False
        ))

# Corners (optional)
fig.add_trace(go.Scatter3d(
    x=[X[0,0], X[0,-1], X[-1,0], X[-1,-1]],
    y=[Y[0,0], Y[0,-1], Y[-1,0], Y[-1,-1]],
    z=[Z[0,0], Z[0,-1], Z[-1,0], Z[-1,-1]],
    mode='markers',
    marker=dict(size=4, color='red', symbol='circle'),
    showlegend=False
))

# Layout
apply_plotly_template(fig)
fig.update_layout(
    title=f"z = {expr}",
    scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=0.5),
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.0))
    ),
    height=650,
    margin=dict(l=0, r=0, t=50, b=0),
    showlegend=False
)

# Animation
if animate:
    frames = []
    for theta in np.linspace(0, 2*np.pi, 40):
        eye = dict(
            x=1.8 * np.cos(theta),
            y=1.8 * np.sin(theta),
            z=1.0 + 0.3 * np.sin(2*theta)
        )
        frames.append(go.Frame(layout=dict(scene_camera=dict(eye=eye))))
    fig.frames = frames
    fig.update_layout(updatemenus=[dict(
        type="buttons",
        buttons=[dict(label="▶", method="animate", args=[None, {"frame": {"duration": 60}}])]
    )])

st.plotly_chart(fig, width='stretch', config=plotly_config())

# --- AI Assistant ---
st.divider()
st.subheader("🤖 Ask about this surface")

question = st.text_input("Ask about this visualisation...", key="ai_question")

if question and st.button("➤ Submit", type="primary"):
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Add & show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 🔥 Fast call — no spinner, instant result
    response = run_ollama_command(question)  # ← fast, blocking, direct

    # Show & store
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})    

   