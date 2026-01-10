import streamlit as st
import requests
import json
import time
import base64
from datetime import datetime
from PIL import Image
import io

st.set_page_config(
    page_title="Z.AI Video Generator Playground",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Z.AI Video Generator Playground")
st.markdown("Test the CogVideoX and Vidu video generation APIs")

# API Configuration
API_URL = "https://api.z.ai/api/paas/v4/videos/generations"
RETRIEVE_URL = "https://api.z.ai/api/paas/v4/async-result/{id}"
API_KEY = "1b86194b06d2434491ff6895c8aa8a87.iEy5dom8ooEzPWQj"

# Session state for task tracking
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'task_status' not in st.session_state:
    st.session_state.task_status = None
if 'task_start_time' not in st.session_state:
    st.session_state.task_start_time = None

# Helper function to convert uploaded file to base64
def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        # Read the file
        bytes_data = uploaded_file.getvalue()
        # Get file extension
        file_type = uploaded_file.type
        # Encode to base64
        base64_string = base64.b64encode(bytes_data).decode('utf-8')
        # Return data URL format
        return f"data:{file_type};base64,{base64_string}"
    return None

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    model_options = {
        "CogVideoX-3": "cogvideox-3",
        "Vidu Text to Video": "viduq1-text",
        "Vidu Image to Video": "viduq1-image",
        "Vidu First & Last Frame": "viduq1-start-end",
        "Vidu Reference to Video": "vidu2-reference"
    }
    
    selected_model_name = st.selectbox(
        "Model",
        list(model_options.keys()),
        index=0,
        help="Choose the video generation model"
    )
    model = model_options[selected_model_name]
    
    # Common parameters
    user_id = st.text_input(
        "User ID (optional)",
        value="test_user_123456",
        help="Unique ID for content filtering (6-128 characters)"
    )
    
    request_id = st.text_input(
        "Request ID (optional)",
        value="",
        help="Unique request identifier"
    )

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input")
    
    # Prompt input
    prompt = st.text_area(
        "Enter your prompt:",
        value="A cat is playing with a ball in a sunny garden.",
        height=100,
        help="Describe the video you want to generate (max 512 characters)"
    )
    
    # Model-specific parameters
    if model == "cogvideox-3":
        st.subheader("CogVideoX-3 Parameters")
        quality = st.selectbox("Quality", ["speed", "quality"], index=0)
        with_audio = st.checkbox("Generate AI sound effects", value=False)
        size = st.selectbox("Size", ["1280x720", "720x1280", "1024x1024", "1080x1920", "1920x1080", "2048x1080", "3840x2160"], index=4)
        fps = st.selectbox("FPS", [30, 60], index=0)
        duration = st.selectbox("Duration (seconds)", [5, 10], index=0)
        
        # Image input for CogVideoX
        image_input_method = st.selectbox("Image Input", ["None", "Upload", "URL"])
        image_url = None
        uploaded_image = None
        
        if image_input_method == "Upload":
            uploaded_image = st.file_uploader(
                "Upload Image", 
                type=['png', 'jpg', 'jpeg'],
                help="Upload an image to use as reference (max 5MB)"
            )
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
                image_url = image_to_base64(uploaded_image)
        elif image_input_method == "URL":
            image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
    
    elif model == "viduq1-text":
        st.subheader("Vidu Text to Video Parameters")
        style = st.selectbox("Style", ["general", "anime"], index=0)
        aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"], index=0)
        size = st.selectbox("Size", ["1920x1080"], index=0)
        duration = st.selectbox("Duration (seconds)", [5], index=0)
        movement_amplitude = st.selectbox("Movement Amplitude", ["auto", "small", "medium", "large"], index=0)
    
    elif model == "viduq1-image":
        st.subheader("Vidu Image to Video Parameters")
        
        # Image input method for Vidu Image to Video
        image_input_method = st.selectbox("Image Input", ["Upload", "URL"])
        uploaded_image = None
        image_url = None
        
        if image_input_method == "Upload":
            uploaded_image = st.file_uploader(
                "Upload Image", 
                type=['png', 'jpg', 'jpeg', 'webp'],
                help="Upload an image to use as first frame (max 50MB)"
            )
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
                image_url = image_to_base64(uploaded_image)
        elif image_input_method == "URL":
            image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg", help="Required: First frame image")
        
        duration = st.selectbox("Duration (seconds)", [5], index=0)
        size = st.selectbox("Size", ["1920x1080"], index=0)
        movement_amplitude = st.selectbox("Movement Amplitude", ["auto", "small", "medium", "large"], index=0)
        with_audio = st.checkbox("Add background music", value=False)
    
    elif model == "viduq1-start-end":
        st.subheader("Vidu First & Last Frame Parameters")
        
        # Frame input method for Vidu First & Last Frame
        frame_input_method = st.selectbox("Frame Input", ["Upload", "URL"])
        uploaded_first_frame = None
        uploaded_last_frame = None
        first_frame_url = None
        last_frame_url = None
        
        if frame_input_method == "Upload":
            col1, col2 = st.columns(2)
            with col1:
                uploaded_first_frame = st.file_uploader(
                    "Upload First Frame", 
                    type=['png', 'jpg', 'jpeg', 'webp'],
                    key="first_frame",
                    help="Upload the first frame image (max 50MB)"
                )
                if uploaded_first_frame:
                    st.image(uploaded_first_frame, caption="First Frame", use_column_width=True)
                    first_frame_url = image_to_base64(uploaded_first_frame)
            
            with col2:
                uploaded_last_frame = st.file_uploader(
                    "Upload Last Frame", 
                    type=['png', 'jpg', 'jpeg', 'webp'],
                    key="last_frame",
                    help="Upload the last frame image (max 50MB)"
                )
                if uploaded_last_frame:
                    st.image(uploaded_last_frame, caption="Last Frame", use_column_width=True)
                    last_frame_url = image_to_base64(uploaded_last_frame)
        elif frame_input_method == "URL":
            first_frame_url = st.text_input("First Frame URL", placeholder="https://example.com/first.jpg")
            last_frame_url = st.text_input("Last Frame URL", placeholder="https://example.com/last.jpg")
        
        duration = st.selectbox("Duration (seconds)", [5], index=0)
        size = st.selectbox("Size", ["1920x1080"], index=0)
        movement_amplitude = st.selectbox("Movement Amplitude", ["auto", "small", "medium", "large"], index=0)
        with_audio = st.checkbox("Add background music", value=False)
    
    elif model == "vidu2-reference":
        st.subheader("Vidu Reference to Video Parameters")
        
        # Reference images input method
        ref_input_method = st.selectbox("Reference Images Input", ["Upload", "URL"])
        uploaded_ref_images = []
        ref_images = None
        
        if ref_input_method == "Upload":
            st.info("Upload 1-3 reference images")
            uploaded_files = st.file_uploader(
                "Upload Reference Images", 
                type=['png', 'jpg', 'jpeg', 'webp'],
                accept_multiple_files=True,
                help="Upload 1-3 reference images (max 50MB each)"
            )
            
            if uploaded_files:
                if len(uploaded_files) > 3:
                    st.warning("Maximum 3 images allowed. Using first 3.")
                    uploaded_files = uploaded_files[:3]
                
                # Display uploaded images
                cols = st.columns(len(uploaded_files))
                for i, uploaded_file in enumerate(uploaded_files):
                    with cols[i]:
                        st.image(uploaded_file, caption=f"Reference {i+1}", use_column_width=True)
                        uploaded_ref_images.append(image_to_base64(uploaded_file))
                
                ref_images = uploaded_ref_images
        elif ref_input_method == "URL":
            st.info("Add 1-3 reference images via URL (comma-separated)")
            ref_text = st.text_input("Reference Image URLs", placeholder="https://example.com/img1.jpg, https://example.com/img2.jpg")
            if ref_text:
                ref_images = [url.strip() for url in ref_text.split(",") if url.strip()]
        
        aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"], index=0)
        size = st.selectbox("Size", ["1280x720"], index=0)
        duration = st.selectbox("Duration (seconds)", [4], index=0)
        movement_amplitude = st.selectbox("Movement Amplitude", ["auto", "small", "medium", "large"], index=0)
        with_audio = st.checkbox("Add background music", value=False)
    
    # Generate button
    generate_button = st.button("🚀 Generate Video", type="primary", use_container_width=True)

with col2:
    st.header("🎥 Output")
    
    # Task status display
    status_placeholder = st.empty()
    
    # Video display placeholder
    video_placeholder = st.empty()
    
    # Metadata placeholder
    metadata_placeholder = st.empty()

# Reset session state when starting a new task
if generate_button:
    st.session_state.task_start_time = None
    if not prompt.strip() and model not in ["viduq1-image", "viduq1-start-end", "vidu2-reference"]:
        st.error("Please enter a prompt!")
        st.stop()
    
    # Validate required fields
    if model == "viduq1-image":
        if not image_url:
            st.error("Image upload or URL is required for Image to Video!")
            st.stop()
    
    if model == "viduq1-start-end" and (not first_frame_url or not last_frame_url):
        st.error("Both first and last frame images are required!")
        st.stop()
    
    if model == "vidu2-reference" and (not ref_images or len(ref_images) == 0):
        st.error("At least one reference image is required!")
        st.stop()
    
    # Validate user_id length if provided
    if user_id and (len(user_id) < 6 or len(user_id) > 128):
        st.error("User ID must be between 6 and 128 characters!")
        st.stop()
    
    # Prepare request payload
    payload = {"model": model}
    
    # Add prompt if provided
    if prompt.strip():
        payload["prompt"] = prompt.strip()
    
    # Add common parameters
    if user_id.strip():
        payload["user_id"] = user_id.strip()
    if request_id.strip():
        payload["request_id"] = request_id.strip()
    
    # Add model-specific parameters
    if model == "cogvideox-3":
        payload.update({
            "quality": quality,
            "with_audio": with_audio,
            "size": size,
            "fps": fps,
            "duration": duration
        })
        if image_url and image_input_method == "URL":
            payload["image_url"] = [image_url]
        elif image_url and image_input_method == "Upload":
            payload["image_url"] = [image_url]
    
    elif model == "viduq1-text":
        payload.update({
            "style": style,
            "aspect_ratio": aspect_ratio,
            "size": size,
            "duration": duration,
            "movement_amplitude": movement_amplitude
        })
    
    elif model == "viduq1-image":
        if not image_url:
            st.error("Image URL is required for Vidu Image to Video!")
            st.stop()
        
        # For viduq1-image, prefer external URL over base64 if base64 is causing issues
        # If image_url starts with 'data:', it's base64, otherwise it's a regular URL
        if image_url.startswith('data:'):
            st.warning("⚠️ Using Base64 images with viduq1-image may cause API errors. Consider using an external image URL instead.")
        
        payload.update({
            "image_url": image_url,
            "duration": duration,
            "size": size,
            "movement_amplitude": movement_amplitude,
            "with_audio": with_audio
        })
        
        # Add prompt if provided (optional for viduq1-image)
        if prompt.strip():
            payload["prompt"] = prompt.strip()
    
    elif model == "viduq1-start-end":
        payload.update({
            "image_url": [first_frame_url, last_frame_url],
            "duration": duration,
            "size": size,
            "movement_amplitude": movement_amplitude,
            "with_audio": with_audio
        })
    
    elif model == "vidu2-reference":
        if ref_images:
            ref_list = [url.strip() for url in ref_images.split(",") if url.strip()]
            if ref_list:
                payload["image_url"] = ref_list
        payload.update({
            "aspect_ratio": aspect_ratio,
            "size": size,
            "duration": duration,
            "movement_amplitude": movement_amplitude,
            "with_audio": with_audio
        })
    
    # Debug: Show payload before sending
    st.write("🔍 **Debug - Request Payload:**")
    st.json(payload)
    
    # Show loading state
    with st.spinner("Submitting video generation request..."):
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("id")
                st.session_state.task_id = task_id
                st.session_state.task_status = "PROCESSING"
                st.session_state.task_start_time = datetime.now()
                
                with status_placeholder.container():
                    st.success(f"✅ Task submitted successfully!")
                    st.write(f"**Task ID:** {task_id}")
                    st.write("**Status:** Processing...")
                    st.write(f"**Started at:** {st.session_state.task_start_time.strftime('%H:%M:%S')}")
                
                # Display initial metadata
                with metadata_placeholder.container():
                    st.subheader("📊 Task Metadata")
                    st.json(result)
                
                # Start polling for results
                st.info("🔄 Polling for results... Video generation may take several minutes.")
                
            elif response.status_code == 429:
                st.error("⏰ Rate Limit Exceeded (429)")
                st.warning("The API has reached its rate limit. Please wait a moment before trying again.")
            
            elif response.status_code == 402:
                st.error("💳 Insufficient Balance (402)")
                st.warning("Your account has insufficient balance or no active resource package.")
                st.info("Please recharge your account to continue using the API.")
            
            else:
                st.error(f"API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    # Check for specific error codes in the response
                    if "error" in error_data and error_data["error"].get("code") == "1113":
                        st.error("💳 Insufficient Balance")
                        st.warning("Your account has insufficient balance or no active resource package.")
                        st.info("Please recharge your account to continue using the API.")
                    else:
                        st.write("Error Details:", error_data)
                except:
                    st.write("Raw Response:", response.text)
        
        except requests.exceptions.RequestException as e:
            st.error(f"Network Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected Error: {str(e)}")

# Polling logic for existing task
if st.session_state.task_id and st.session_state.task_status == "PROCESSING":
    task_id = st.session_state.task_id
    
    # Add a button to manually refresh
    if st.button("🔄 Check Status", key="refresh_status"):
        with st.spinner("Checking task status..."):
            try:
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                
                retrieve_url = RETRIEVE_URL.format(id=task_id)
                response = requests.get(retrieve_url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    task_status = result.get("task_status", "UNKNOWN")
                    st.session_state.task_status = task_status
                    
                    # Calculate processing time
                    processing_time = None
                    if st.session_state.task_start_time:
                        current_time = datetime.now()
                        processing_time = current_time - st.session_state.task_start_time
                        time_seconds = processing_time.total_seconds()
                        time_minutes = time_seconds // 60
                        time_seconds_remaining = time_seconds % 60
                        
                        if task_status == "SUCCESS":
                            time_str = f"{int(time_minutes)}m {int(time_seconds_remaining)}s"
                        else:
                            time_str = f"{int(time_seconds)}s"
                    
                    with status_placeholder.container():
                        if task_status == "SUCCESS":
                            st.success("✅ Video generation completed!")
                            st.info(f"⏱️ **Processing Time:** {time_str}")
                        elif task_status == "FAIL":
                            st.error("❌ Video generation failed!")
                            if processing_time:
                                st.info(f"⏱️ **Time until failure:** {time_str}")
                        else:
                            st.info(f"⏳ Status: {task_status}")
                            if processing_time:
                                st.info(f"⏱️ **Elapsed time:** {time_str}")
                        
                        st.write(f"**Task ID:** {task_id}")
                        st.write(f"**Status:** {task_status}")
                        if st.session_state.task_start_time:
                            st.write(f"**Started at:** {st.session_state.task_start_time.strftime('%H:%M:%S')}")
                    
                    # Display video if successful
                    if task_status == "SUCCESS" and "video_result" in result:
                        video_results = result["video_result"]
                        if video_results and len(video_results) > 0:
                            video_data = video_results[0]
                            video_url = video_data.get("url")
                            cover_url = video_data.get("cover_image_url")
                            
                            with video_placeholder.container():
                                st.subheader("🎥 Generated Video")
                                
                                # Display video
                                if video_url:
                                    st.video(video_url)
                                
                                # Display cover image if available
                                if cover_url:
                                    st.image(cover_url, caption="Video Cover", use_column_width=True)
                                
                                # Display URLs
                                st.write(f"**Video URL:** {video_url}")
                                if cover_url:
                                    st.write(f"**Cover URL:** {cover_url}")
                    
                    # Update metadata
                    with metadata_placeholder.container():
                        st.subheader("📊 Task Details")
                        st.json(result)
                
                elif response.status_code == 429:
                    st.warning("⏰ Rate limit reached while checking status. Please wait before refreshing.")
                
                elif response.status_code == 402:
                    st.error("💳 Insufficient Balance")
                    st.warning("Your account has insufficient balance or no active resource package.")
                    st.info("Please recharge your account to continue using the API.")
                
                else:
                    st.error(f"Error checking status: {response.status_code}")
                    try:
                        error_data = response.json()
                        # Check for specific error codes in the response
                        if "error" in error_data and error_data["error"].get("code") == "1113":
                            st.error("💳 Insufficient Balance")
                            st.warning("Your account has insufficient balance or no active resource package.")
                            st.info("Please recharge your account to continue using the API.")
                        else:
                            st.write("Error Details:", error_data)
                    except:
                        st.write("Raw Response:", response.text)
            
            except requests.exceptions.RequestException as e:
                st.error(f"Network Error while checking status: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected Error while checking status: {str(e)}")

# Auto-refresh option
if st.session_state.task_id and st.session_state.task_status == "PROCESSING":
    auto_refresh = st.checkbox("🔄 Auto-refresh every 10 seconds", value=False)
    if auto_refresh:
        time.sleep(10)
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    **API Documentation:** Based on Z.AI CogVideoX and Vidu Video Generation APIs  
    **Note:** Video generation is asynchronous and may take several minutes to complete.
    """
)

# Quick examples section
st.header("💡 Quick Examples")
examples = [
    "A cat is playing with a ball in a sunny garden",
    "A futuristic city with flying cars and neon lights at night",
    "A peaceful forest with a small stream and sunlight filtering through trees",
    "An astronaut walking on Mars with Earth visible in the sky",
    "A steaming cup of coffee on a wooden table next to an open book"
]

selected_example = st.selectbox("Try these examples:", [""] + examples)
if selected_example and st.button("Use Example"):
    st.session_state.prompt = selected_example
    st.rerun()
