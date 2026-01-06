import streamlit as st
import os
import time
from markitdown import MarkItDown
import pandas as pd

# --- Configuration & Setup ---
st.set_page_config(page_title="Universal File-to-Text Converter", page_icon="📄")

# Initialize MarkItDown
md = MarkItDown()

def save_uploaded_file(uploaded_file):
    """Save upload to temp file for processing."""
    try:
        temp_dir = "temp_processing"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        return None

def convert_file(file_path):
    """Safe conversion wrapper."""
    try:
        result = md.convert(file_path)
        return result.text_content
    except Exception:
        return None

def format_size(size_in_bytes):
    """Converts bytes to readable KB or MB."""
    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

# --- UI Layout ---
st.title("📄 Universal File-to-Markdown Converter")
st.markdown("Upload your **Word, Excel, PowerPoint, PDF, or HTML** files below.")

uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    accept_multiple_files=True,
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'zip', 'txt', 'csv']
)

if uploaded_files:
    st.divider()
    
    for uploaded_file in uploaded_files:
        with st.container():
            st.subheader(f"Processing: {uploaded_file.name}")
            
            # 1. Save and Convert
            temp_path = save_uploaded_file(uploaded_file)
            
            if temp_path:
                converted_text = convert_file(temp_path)
                
                if converted_text is None:
                     st.warning(f"⚠️ Could not read **{uploaded_file.name}**. Please check the format.")
                else:
                    # Create Tabs for View Switching
                    tab1, tab2 = st.tabs(["📄 Preview & Download", "📊 File Size Comparison"])
                    
                    # --- TAB 1: PREVIEW & DOWNLOAD ---
                    with tab1:
                        st.text_area(f"Preview content", converted_text, height=200)
                        
                        base_name = os.path.splitext(uploaded_file.name)[0]
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="⬇️ Download Markdown (.md)",
                                data=converted_text,
                                file_name=f"{base_name}_converted.md",
                                mime="text/markdown"
                            )
                        with col2:
                            st.download_button(
                                label="⬇️ Download Text (.txt)",
                                data=converted_text,
                                file_name=f"{base_name}_converted.txt",
                                mime="text/plain"
                            )

                    # --- TAB 2: FILE SIZE COMPARISON ---
                    with tab2:
                        # Calculate Sizes
                        original_size = uploaded_file.size
                        
                        # FIXED LINE BELOW
                        converted_size = len(converted_text.encode('utf-8'))
                        
                        # Calculate Percentage Reduction
                        if original_size > 0:
                            reduction = ((original_size - converted_size) / original_size) * 100
                        else:
                            reduction = 0
                            
                        # Display Comparison Table
                        data = {
                            "Metric": ["Original File Size", "Converted Text Size"],
                            "Size": [format_size(original_size), format_size(converted_size)]
                        }
                        df = pd.DataFrame(data)
                        
                        st.table(df)
                        
                        # Display Percentage Badge
                        if reduction > 0:
                            st.success(f"🚀 Text version is **{reduction:.1f}% smaller** than the original!")
                        elif reduction < 0:
                            st.info(f"ℹ️ Text version is larger (common for very small compressed files).")
                        else:
                            st.info("File sizes are identical.")

                # Cleanup
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            st.divider()

# Sidebar
with st.sidebar:
    st.info("Supported Formats: .docx, .xlsx, .pptx, .pdf, .html, .zip")
