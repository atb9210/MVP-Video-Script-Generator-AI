import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
from datetime import datetime

st.set_page_config(
    page_title="Z.AI Image Generator Playground",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Z.AI Image Generator Playground")
st.markdown("Test the CogView-4 image generation API")

# API Configuration
API_URL = "https://api.z.ai/api/paas/v4/images/generations"
API_KEY = "1b86194b06d2434491ff6895c8aa8a87.iEy5dom8ooEzPWQj"

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["cogview-4-250304"],
        help="CogView-4 model for image generation"
    )
    
    # Quality selection
    quality = st.selectbox(
        "Quality",
        ["standard", "hd"],
        index=0,
        help="HD quality takes ~20s, Standard takes ~5-10s"
    )
    
    # Size selection
    size_options = ["1024x1024", "768x1344", "864x1152", "1344x768", "1152x864", "1440x720", "720x1440"]
    size = st.selectbox(
        "Size",
        size_options,
        index=0,
        help="Image dimensions in pixels"
    )
    
    # User ID (optional)
    user_id = st.text_input(
        "User ID (optional)",
        value="test_user_123456",
        help="Unique ID for content filtering (6-128 characters)"
    )

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input")
    
    # Prompt input
    prompt = st.text_area(
        "Enter your prompt:",
        value="A cute little kitten sitting on a sunny windowsill, with the background of blue sky and white clouds.",
        height=150,
        help="Describe the image you want to generate"
    )
    
    # Generate button
    generate_button = st.button("🚀 Generate Image", type="primary", use_container_width=True)

with col2:
    st.header("🖼️ Output")
    
    # Placeholder for generated image
    image_placeholder = st.empty()
    
    # Placeholder for metadata
    metadata_placeholder = st.empty()

# Generation logic
if generate_button:
    if not prompt.strip():
        st.error("Please enter a prompt!")
        st.stop()
    
    # Validate user_id length if provided
    if user_id and (len(user_id) < 6 or len(user_id) > 128):
        st.error("User ID must be between 6 and 128 characters!")
        st.stop()
    
    # Show loading state
    with st.spinner("Generating image... This may take 5-20 seconds depending on quality setting."):
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt.strip(),
                "quality": quality,
                "size": size
            }
            
            # Add user_id if provided
            if user_id.strip():
                payload["user_id"] = user_id.strip()
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display the generated image
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0]["url"]
                    
                    # Try to download and display the image
                    try:
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            # Display image from downloaded content
                            image_placeholder.image(img_response.content, caption="Generated Image", use_column_width=True)
                        else:
                            # Fallback to URL display with error message
                            image_placeholder.image(image_url, caption="Generated Image (URL may not display)", use_column_width=True)
                            st.warning("⚠️ Image downloaded but may not display properly. Use the URL below to view/download.")
                    except Exception as e:
                        # Fallback to URL display
                        image_placeholder.image(image_url, caption="Generated Image (URL may not display)", use_column_width=True)
                        st.warning(f"⚠️ Could not download image for display: {str(e)}")
                        st.info("Use the URL below to view/download the image directly.")
                    
                    # Display metadata
                    with metadata_placeholder.container():
                        st.subheader("📊 Metadata")
                        
                        # Creation time
                        if "created" in result:
                            created_time = datetime.fromtimestamp(result["created"])
                            st.write(f"**Created:** {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Image URL
                        st.write(f"**Image URL:** {image_url}")
                        
                        # Request details
                        st.write("**Request Details:**")
                        st.json(payload)
                        
                        # Content filter info
                        if "content_filter" in result:
                            st.write("**Content Filter:**")
                            st.json(result["content_filter"])
                
                else:
                    st.error("No image data in response!")
                    st.write("Response:", result)
            
            elif response.status_code == 429:
                st.error("⏰ Rate Limit Exceeded (429)")
                st.warning("The API has reached its rate limit. Please wait a moment before trying again.")
                st.info("This is a common issue with API services - try again in a few minutes.")
            
            else:
                st.error(f"API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    st.write("Error Details:", error_data)
                except:
                    st.write("Raw Response:", response.text)
        
        except requests.exceptions.RequestException as e:
            st.error(f"Network Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    **API Documentation:** Based on Z.AI CogView-4 Image Generation API  
    **Note:** Generated image URLs expire after 30 days. Save important images locally.
    """
)

# Quick examples section
st.header("💡 Quick Examples")
examples = [
    "A majestic dragon flying over a medieval castle at sunset",
    "A futuristic city with flying cars and neon lights",
    "A peaceful forest scene with a small stream and sunlight filtering through trees",
    "An astronaut standing on Mars with Earth visible in the sky",
    "A steaming cup of coffee on a wooden table next to an open book"
]

selected_example = st.selectbox("Try these examples:", [""] + examples)
if selected_example and st.button("Use Example"):
    st.session_state.prompt = selected_example
    st.rerun()
