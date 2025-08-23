import os
import google.generativeai as genai
import yaml
import csv
import json
from datetime import datetime
import re
from sentiment import analyze_sentiment

# Load API key from environment (do not hardcode secrets)
api_key = "API-KEY"

# Configure the API
genai.configure(api_key=api_key)

# Load data from YAML files
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load brands
brands_path = os.path.join(base_dir, "brands.yaml")
with open(brands_path, "r", encoding="utf-8") as f:
    brands = yaml.safe_load(f).get("brands", [])

# Load prompts
prompts_path = os.path.join(base_dir, "prompts.yaml")
with open(prompts_path, "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f).get("prompts", [])

# Create model
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def analyze_mentions(text, brand_obj):
    """Count brand and competitor mentions in the AI response."""
    results = {
        "brand": brand_obj["canonical"],
        "brand_mentions": 0,
        "competitor_mentions": {}
    }
    
    # Count brand mentions (case-insensitive)
    text_lower = text.lower()
    
    # Count canonical brand name and variants
    for variant in [brand_obj["canonical"]] + brand_obj["variants"]:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(variant.lower()) + r'\b'
        matches = re.findall(pattern, text_lower)
        results["brand_mentions"] += len(matches)
    
    # Count competitor mentions
    for competitor in brand_obj["competitors"]:
        pattern = r'\b' + re.escape(competitor.lower()) + r'\b'
        matches = re.findall(pattern, text_lower)
        results["competitor_mentions"][competitor] = len(matches)
    
    return results

def query_ai_for_brand(brand_name, variants, competitors, prompt_text):
    """Query AI with brand context."""
    # Create a context-aware prompt
    context = f"""
    Focus on analyzing the brand "{brand_name}" (also known as: {', '.join(variants)}).
    Consider its competitors: {', '.join(competitors)}.
    
    {prompt_text}
    """
    
    response = model.generate_content(context)
    return response.text

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(results_dir, f"brand_analysis_{timestamp}.csv")
    
    print(f"Starting brand analysis... Results will be saved to: {csv_filename}")
    
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "prompt_id", 
            "brand", 
            "brand_mentions", 
            "competitor_mentions", 
            "raw_response",
            "sentiment_score",
            "sentiment_label"   
        ])
        writer.writeheader()
        
        for brand_obj in brands:
            brand_name = brand_obj["canonical"]
            print(f"\n{'='*50}")
            print(f"Analyzing brand: {brand_name}")
            print(f"{'='*50}")
            
            for prompt in prompts:
                print(f"\n--- Running Prompt: {prompt['id']} for {brand_name} ---")
                
                # Query AI with brand context
                try:
                    response_text = query_ai_for_brand(
                        brand_name, 
                        brand_obj["variants"], 
                        brand_obj["competitors"], 
                        prompt["text"]
                    )
                    
                    print(f"Q: {prompt['text']}")
                    print(f"A: {response_text[:200]}..." if len(response_text) > 200 else f"A: {response_text}")
                    
                    # Analyze mentions
                    mentions = analyze_mentions(response_text, brand_obj)
                    
                    # Analyze sentiment
                    sentiment = analyze_sentiment(response_text)
                    
                    print(f"Brand mentions: {mentions['brand_mentions']}")
                    print(f"Competitor mentions: {mentions['competitor_mentions']}")
                    print(f"Sentiment: {sentiment['label']} (score: {sentiment['polarity']:.3f})")
                    
                    # Write to CSV
                    writer.writerow({
                        "prompt_id": prompt["id"],
                        "brand": brand_name,
                        "brand_mentions": mentions["brand_mentions"],
                        "competitor_mentions": json.dumps(mentions["competitor_mentions"]),  # Convert dict to JSON string
                        "raw_response": response_text,
                        "sentiment_score": sentiment["polarity"],
                        "sentiment_label": sentiment["label"]
                    })
                    
                except Exception as e:
                    print(f"Error processing {brand_name} with prompt {prompt['id']}: {e}")
                    continue
    
    print(f"\n{'='*50}")
    print(f"Analysis complete! Results saved to: {csv_filename}")
    print(f"{'='*50}")
