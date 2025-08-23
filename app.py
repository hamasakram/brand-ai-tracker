import os
import yaml
import csv
import json
import re
from datetime import datetime
import streamlit as st
import pandas as pd
import google.generativeai as genai
from sentiment import analyze_sentiment

# Configure API key
api_key = os.getenv("GEMINI_API_KEY", "API-KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# --- Functions ---
def analyze_mentions(text, brand_obj):
    results = {
        "brand": brand_obj["canonical"],
        "brand_mentions": 0,
        "competitor_mentions": {}
    }
    text_lower = text.lower()
    for variant in [brand_obj["canonical"]] + brand_obj["variants"]:
        pattern = r'\b' + re.escape(variant.lower()) + r'\b'
        results["brand_mentions"] += len(re.findall(pattern, text_lower))
    for competitor in brand_obj["competitors"]:
        pattern = r'\b' + re.escape(competitor.lower()) + r'\b'
        results["competitor_mentions"][competitor] = len(re.findall(pattern, text_lower))
    return results

def query_ai_for_brand(brand_name, variants, competitors, prompt_text):
    context = f"""
    Focus on analyzing the brand "{brand_name}" (also known as: {', '.join(variants)}).
    Consider its competitors: {', '.join(competitors)}.
    
    {prompt_text}
    """
    response = model.generate_content(context)
    return response.text

# --- Streamlit UI ---
st.set_page_config(page_title="Brand Tracker", page_icon="🤖", layout="wide")

st.title("🤖 Brand Tracker with Gemini + Sentiment Analysis")
st.markdown("---")

# Sidebar for file uploads
with st.sidebar:
    st.header("📁 Upload Files")
    brands_file = st.file_uploader("Upload brands.yaml", type="yaml")
    prompts_file = st.file_uploader("Upload prompts.yaml", type="yaml")
    
    # Show sample data structure
    if not brands_file or not prompts_file:
        st.info("💡 **Need sample files?** Use the ones in your project folder:")
        st.code("brands.yaml\nprompts.yaml", language="text")

# Main content area
if brands_file and prompts_file:
    try:
        brands = yaml.safe_load(brands_file).get("brands", [])
        prompts = yaml.safe_load(prompts_file).get("prompts", [])
        
        if not brands or not prompts:
            st.error("❌ No brands or prompts found in the uploaded files!")
        else:
            st.success(f"✅ Loaded {len(brands)} brands and {len(prompts)} prompts")
            
            # Show loaded data
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Brands Loaded")
                for brand in brands:
                    st.write(f"**{brand['canonical']}** - Variants: {', '.join(brand['variants'])}")
                    st.write(f"Competitors: {', '.join(brand['competitors'])}")
                    st.write("---")
            
            with col2:
                st.subheader("💬 Prompts Loaded")
                for prompt in prompts:
                    st.write(f"**{prompt['id']}**: {prompt['text']}")
                    st.write("---")
            
            # Analysis button
            if st.button("🚀 Run Brand Analysis", type="primary"):
                with st.spinner("Analyzing brands with Gemini AI..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    total_analyses = len(brands) * len(prompts)
                    current_analysis = 0
                    
                    for brand_obj in brands:
                        for prompt in prompts:
                            try:
                                # Update progress
                                current_analysis += 1
                                progress_bar.progress(current_analysis / total_analyses)
                                
                                # Query AI
                                response_text = query_ai_for_brand(
                                    brand_obj["canonical"],
                                    brand_obj["variants"],
                                    brand_obj["competitors"],
                                    prompt["text"]
                                )
                                
                                # Analyze mentions and sentiment
                                mentions = analyze_mentions(response_text, brand_obj)
                                sentiment = analyze_sentiment(response_text)
                                
                                results.append({
                                    "prompt_id": prompt["id"],
                                    "brand": brand_obj["canonical"],
                                    "brand_mentions": mentions["brand_mentions"],
                                    "competitor_mentions": json.dumps(mentions["competitor_mentions"]),
                                    "sentiment_score": sentiment["polarity"],
                                    "sentiment_label": sentiment["label"],
                                    "raw_response": response_text
                                })
                                
                                st.success(f"✅ Analyzed {brand_obj['canonical']} with prompt '{prompt['id']}'")
                                
                            except Exception as e:
                                st.error(f"❌ Error analyzing {brand_obj['canonical']}: {str(e)}")
                                continue
                    
                    progress_bar.empty()
                    
                    if results:
                        st.success(f"🎉 Analysis complete! Generated {len(results)} results")
                        
                        # Convert to DataFrame and display
                        df = pd.DataFrame(results)
                        st.subheader("📊 Analysis Results")
                        st.dataframe(df, use_container_width=True)
                        
                        # Download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        csv_filename = f"brand_analysis_{timestamp}.csv"
                        df.to_csv(csv_filename, index=False)
                        
                        with open(csv_filename, "rb") as f:
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=f.read(),
                                file_name=csv_filename,
                                mime="text/csv"
                            )
                    else:
                        st.error("❌ No results generated. Please check your files and try again.")
                        
    except Exception as e:
        st.error(f"❌ Error loading files: {str(e)}")
        st.info("Make sure your YAML files are properly formatted.")

else:
    # Default content when no files are uploaded
    st.markdown("""
    ## 🚀 Welcome to Brand Tracker!
    
    This app analyzes brands using Google's Gemini AI and provides sentiment analysis.
    
    ### 📋 What you need:
    1. **brands.yaml** - Contains your brand definitions
    2. **prompts.yaml** - Contains your analysis prompts
    
    ### 🔧 How to use:
    1. Upload both YAML files using the sidebar
    2. Click "Run Brand Analysis" 
    3. Download your results as CSV
    
    ### 📁 Sample file structure:
    
    **brands.yaml:**
    ```yaml
    brands:
      - canonical: "Acme"
        variants: ["Acme Inc", "AcmeCo"]
        competitors: ["Globex", "Umbrella"]
    ```
    
    **prompts.yaml:**
    ```yaml
    prompts:
      - id: "top_brands"
        text: "What are the best project management software brands in 2025?"
    ```
    """)
    
    # Show current project files
    st.subheader("📁 Current Project Files")
    if os.path.exists("brands.yaml") and os.path.exists("prompts.yaml"):
        st.success("✅ Found brands.yaml and prompts.yaml in your project folder!")
        
        # Load and display current files
        try:
            with open("brands.yaml", "r") as f:
                brands_content = f.read()
            with open("prompts.yaml", "r") as f:
                prompts_content = f.read()
                
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Current brands.yaml")
                st.code(brands_content, language="yaml")
            with col2:
                st.subheader("Current prompts.yaml")
                st.code(prompts_content, language="yaml")
                
        except Exception as e:
            st.error(f"Error reading files: {str(e)}")
    else:
        st.warning("⚠️ No YAML files found in current directory")
