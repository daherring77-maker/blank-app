import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Plotly Visualizations",
    page_icon="📊",
    layout="wide"
)
# ----------------------------
# Main App
# ----------------------------
st.title("🌌 Mathematical Visualisations Gallery")
st.markdown("""
Explore the hidden geometry of chaos, symmetry, and growth —  
all rendered in real-time with Plotly.
""")

# Mini previews (static images or Plotly thumbnails)
col1, col2, col3 = st.columns(3)
with col1:
    st.image("lorenz_thumb.png", caption="Lorenz Attractor", width='stretch')
with col2:
    st.image("snowflake_thumb.png", caption="Snowflake Generator",  width='stretch')
with col3:
    st.image("fern_thumb.png", caption="Barnsley Fern",  width='stretch')

st.divider()
st.subheader("✨ Featured Explorations")
st.page_link("pages/lorenz.py", label="🌀 Chaos & Attractors", icon="🌀")
st.page_link("pages/snowflake.py", label="❄️ Symmetry & Snowflakes", icon="❄️")
st.page_link("pages/fern.py", label="🌿 Fractals & Nature", icon="🌿")

pages = {
        "Visualisations": [
           st.Page("pages/lorenz.py", title="Lorenz Attractor", icon="🔧"),
           st.Page("pages/klein.py", title="Klein Bottle", icon="🔧"), 
           st.Page("pages/snowflake.py", title="Snowflake Generator", icon="🔧"),
           st.Page("pages/snowflake_parametric.py", title="3D Surface", icon="🔧"), 
           st.Page("pages/wireframe.py", title="Wireframe", icon="🔧"),
           st.Page("pages/spiral.py", title="Archimedes Spiral", icon="🔧"),
           st.Page("pages/surface_trefoil.py", title="Trefoil Knot", icon="🔧"),
           st.Page("pages/helical_cylinder.py", title="Helical Cylinder", icon="🔧"),
           st.Page("pages/fern.py", title="Barnsley Fern", icon="🔧")
        ] 
}
pg = st.navigation(pages)
pg.run()
