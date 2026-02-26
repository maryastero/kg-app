import streamlit as st
import streamlit.components.v1 as components
from generate_knowledge_graph import generate_knowledge_graph
import os

st.set_page_config(layout="wide", page_title="Bio-Genomic KG Creator", page_icon="🧬")

# --- CUSTOM CSS ---
st.markdown("""<style> .main { background-color: #1a1a1a; } </style>""", unsafe_allow_html=True)

st.title("🧬 Genomic Knowledge Graph Creator")
st.markdown("Convert complex biological text into interactive relationship maps using GPT-4o.")

# Initialize Session State for the graph
if 'html_graph' not in st.session_state:
    st.session_state.html_graph = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Input Data")
    input_method = st.radio("Method:", ["Text Input", "File Upload"])
    
    if input_method == "File Upload":
        uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])
        text = uploaded_file.read().decode("utf-8") if uploaded_file else ""
    else:
        text = st.text_area("Paste Bio-Text here:", height=300, 
                            placeholder="e.g., BRCA1 interacts with BARD1...")

    generate_btn = st.button("🚀 Build Knowledge Graph", use_container_width=True)

# --- MAIN LOGIC ---
if generate_btn and text:
    with st.spinner("🧬 AI is identifying biological entities..."):
        try:
            # 1. Generate Graph
            net = generate_knowledge_graph(text)
            
            # 2. Save to string/file
            path = "temp_graph.html"
            net.save_graph(path)
            with open(path, 'r', encoding='utf-8') as f:
                st.session_state.html_graph = f.read()
            
            st.toast("Graph built successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error: {e}")

# --- DISPLAY ---
if st.session_state.html_graph:
    # Action Buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        st.download_button(
            label="💾 Download HTML",
            data=st.session_state.html_graph,
            file_name="bio_knowledge_graph.html",
            mime="text/html"
        )
    
    # Render the Graph
    components.html(st.session_state.html_graph, height=800, scrolling=False)
    
    with st.expander("🔍 How to read this graph?"):
        st.write("""
        - **Node Size:** Larger nodes have more biological interactions (Hubs).
        - **Colors:** Blue = Genes, Green = Proteins, Red = Diseases.
        - **Interaction:** Drag nodes to organize them; scroll to zoom.
        """)
else:
    st.info("Point to a text source in the sidebar and click 'Build' to begin.")
