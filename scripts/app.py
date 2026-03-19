import os
import sys
sys.path.append(os.path.dirname(__file__))
from PIL import Image
import numpy as np
from utils import predict_disease,say_disease,resize_and_rescale,get_available_voices,speak_text_with_settings
import streamlit as st


# Configure page


st.set_page_config(
    page_title="BotanIQ - Tomato Disease Detector",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        min-height: 100vh;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    .main-header {
        text-align: center;
        color: #ffffff;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #e0e0e0;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .disease-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .healthy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .disease-name {
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .confidence {
        font-size: 1.2em;
        margin-top: 10px;
        padding: 10px;
        background: rgba(255,255,255,0.2);
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## About BotanIQ")
    st.info("""
    **BotanIQ** uses AI to detect diseases in tomato plant leaves.
    
    Supported diseases include:
    - 🔴 Bacterial Spot
    - 🟤 Early Blight
    - ⚫ Late Blight
    - ⚪ Septoria Leaf Spot
    - 🟢 Healthy Leaves
    """)
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("""
    1. Upload a clear photo of a tomato leaf
    2. Click 'Submit' to analyze
    3. Get instant diagnosis and management practices + audio description
    """)
    
    st.markdown("---")
    st.markdown("### 🎤 Voice Settings")
    
    # Initialize session state for voice settings
    if 'voice_settings' not in st.session_state:
        st.session_state.voice_settings = {
            'voice_index': 0,
            'speed': 0,      # mapped rate (-10..10), default normal
            'volume': 100,   # percent 0-100
        }
    
    # Voice selection
    voices = get_available_voices()
    if len(voices) == 1 and voices[0] == "Default Voice":
        st.warning("No system voices detected; audio will be disabled.")
    voice_names = [f"{i+1}. {voice}" for i, voice in enumerate(voices)]
    selected_voice = st.selectbox(
        "Choose Voice:",
        options=range(len(voices)),
        format_func=lambda x: voice_names[x],
        index=st.session_state.voice_settings['voice_index'],
        help="Select a voice for audio descriptions"
    )
    
    # Rate setting (-10 slowest, 0 normal, +10 fastest)
    rate = st.slider(
        "Speech Rate:",
        min_value=-10,
        max_value=10,
        value=st.session_state.voice_settings.get('speed', 5),
        step=1,
        help="Adjust how fast the voice speaks: negative values slow it down, positive speed it up"
    )
    
    # Volume setting (0-100 percent)
    volume = st.slider(
        "Volume (0-100):",
        min_value=0,
        max_value=100,
        value=st.session_state.voice_settings['volume'],
        step=1,
        help="Adjust the volume of the voice"
    )
    
    # Update session state when settings change
    st.session_state.voice_settings['voice_index'] = selected_voice
    st.session_state.voice_settings['speed'] = rate
    st.session_state.voice_settings['volume'] = volume
    
    # Test voice button
    if st.button("🔊 Test Voice", help="Hear a sample of the selected voice"):
        test_text = "This is a test of the BotanIQ voice system. The tomato plant appears healthy."
        audio_path = speak_text_with_settings(test_text, selected_voice, rate, volume)
        if audio_path:
            st.audio(audio_path, format="audio/wav")
            st.success("Voice test played!")
        else:
            st.error("TTS failed - no audio generated")

# Main interface
st.markdown('<div class="main-header"><span style="color: #ffffff;">Botan</span><span style="color: #00ff88;">IQ🍀</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced Tomato Plant Disease Detector</div>', unsafe_allow_html=True)

# allow user to choose input method
mode = st.radio("Choose input method:", ["Upload Image", "Use Device Camera"], index=0, horizontal=True)

input_image = None

if False:  # no live webcam option any more
    pass
else:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Provide Leaf Image")
        uploaded_file = None
        camera_file = None
        if mode == "Upload Image":
            uploaded_file = st.file_uploader("Choose a tomato leaf image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Image", width=400)
        else:
            st.markdown("### Capture from Camera")
            camera_file = st.camera_input("Take a photo of your leaf")
            if camera_file is not None:
                st.image(camera_file, caption="Captured Image", width=400)

    with col2:
        st.markdown("### 🔍 Analysis Results")
        st.info("Provide an image via upload or webcam and click Submit to see results here")

    process_button = st.button("Submit for Analysis", help="Analyze the provided leaf image", use_container_width=True)

    # determine which image to send
    if process_button:
        if mode == "Upload Image":
            input_image = uploaded_file
        else:
            input_image = camera_file

    if process_button and input_image is not None:
        with st.spinner("Analyzing leaf..."):
            try:
                pred_vector = predict_disease(input_image)
            except Exception as e:
                st.error(f"Model loading/prediction failed: {e}")
                st.stop()

            if pred_vector is None:
                st.error("Prediction failed: the model did not return results.")
                st.stop()

            prediction_index = np.argmax(pred_vector, axis=1)[0].item()
            # speak using TTS and capture audio path
            # convert slider->rate before calling say_disease
            prediction, audio_file = say_disease(prediction_index)

            # display results (no columns needed since audio column removed)
            disease_names = {
                0: "Bacterial Spot",
                1: "Early Blight", 
                2: "Late Blight",
                3: "Septoria Leaf Spot",
                4: "Healthy Tomato"
            }
            is_healthy = prediction_index == 4
            card_class = "disease-card healthy" if is_healthy else "disease-card"
            conf = round(max(pred_vector[0]) * 100, 1)
            st.markdown(f"""
            <div class="{card_class}">
                <div class="disease-name">{disease_names[prediction_index]}</div>
                <div class="confidence">Confidence: {conf}%</div>
            </div>
            """, unsafe_allow_html=True)

        # Expandable details (includes audio player)
        with st.expander("Disease Details & Management", expanded=False):
            st.markdown(prediction)
            if audio_file:
                st.audio(audio_file, format="audio/wav")
        
            
    elif process_button and input_image is None:
        st.error("Please provide an image using the selected method.")
  



