# BotanIQ - Tomato Plant Disease Detection AI

An AI-powered mobile-friendly web application for identifying tomato plant diseases using computer vision and machine learning. Perfect for farmers, gardeners, and agricultural professionals.

## 🌟 Features

- **Disease Detection**: Identifies 5 tomato diseases with high accuracy
- **Mobile Optimized**: Works on phones, tablets, and desktops
- **Offline Capable**: Runs completely offline after initial setup
- **Voice Feedback**: Audio descriptions of diagnoses
- **Real-time Analysis**: Instant results from leaf photos
- **User-friendly Interface**: Simple upload and analyze workflow

## 📱 Mobile Usage

### ✅ **Works on Mobile Phones**

BotanIQ is designed to work seamlessly on mobile devices:

- **Camera Integration**: Take photos directly from your phone's camera
- **Touch Optimized**: Large buttons and mobile-friendly interface
- **Responsive Design**: Adapts to any screen size
- **Fast Loading**: Optimized for mobile networks and data usage

### 🔄 **Offline Mobile Usage**

**Yes, BotanIQ works completely offline on mobile devices!**

#### What Works Offline:
- ✅ Disease detection and analysis
- ✅ Voice feedback (on supported mobile browsers)
- ✅ All core functionality
- ✅ Saved model predictions

#### What Requires Internet (One-time):
- ⏳ Initial app loading and model download
- ⏳ Streamlit server connection (if running remotely)

### 📲 **Mobile Deployment Options**

#### Option 1: Local Network Access (Recommended)
```bash
# Run on your computer
streamlit run scripts/app.py

# Access from phone via local network:
# http://YOUR_COMPUTER_IP:8501
```

#### Option 2: Cloud Deployment
Deploy to services like:
- **Streamlit Cloud** (free tier available)
- **Heroku**
- **AWS/GCP/Azure**
- **Railway** or **Render**

**Recommended cloud build/start commands**

```bash
pip install --upgrade pip
pip install -r requirements.txt
streamlit run scripts/app.py --server.port $PORT --server.headless true --server.address 0.0.0.0
```

#### Option 3: Mobile App Conversion
Convert to native app using:
- **PWA** (Progressive Web App) capabilities
- **Capacitor** or **Cordova** for native apps
- **React Native** rebuild

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Windows/macOS/Linux
- 4GB+ RAM recommended

### Installation

1. **Clone/Download the project**
   ```bash
   git clone <repository-url>
   cd botanq_ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure HuggingFace token**
   Create `.streamlit/secrets.toml`:
   ```toml
   HF_TOKEN = "your_huggingface_token_here"
   ```
   Get a token at: https://huggingface.co/settings/tokens

5. **Run the app**
   ```bash
   streamlit run scripts/app.py
   ```

   The app will open at `http://localhost:8501`

## 📱 Using on Mobile

### Method 1: Local Network Access
1. Run the app on your computer as described above
2. Find your computer's IP address:
   - Windows: `ipconfig` in Command Prompt
   - macOS: `ifconfig` in Terminal
   - Linux: `ip addr show`
3. On your phone, open browser and go to: `http://YOUR_IP:8501`

### Method 2: Direct Phone Access
If running on the same device:
- Use `http://localhost:8501` on the device itself
- Or use `http://127.0.0.1:8501`

### Method 3: Cloud Deployment
Deploy to a cloud service and access via public URL from any device.

## 🔊 Text-to-Speech (TTS)

### Desktop (Windows)
- Uses Windows built-in System.Speech API
- No extra packages required
- Works completely offline
- Multiple voice options available

### Mobile Browsers
- Uses browser's built-in speech synthesis
- May require user permission for audio
- Works offline after page loads
- Voice quality depends on device/browser

## 📊 Supported Diseases

1. **Bacterial Spot** - Small dark spots with yellow halos
2. **Early Blight** - Dark spots with concentric rings
3. **Late Blight** - Water-soaked lesions, white mold
4. **Septoria Leaf Spot** - Small circular spots with dark borders
5. **Healthy** - No disease symptoms

## 🛠️ Troubleshooting

### Common Issues

**App won't load on mobile:**
- Check firewall settings
- Ensure both devices are on same network
- Try different browser (Chrome recommended)

**TTS not working:**
- On mobile: Check browser permissions for audio
- On desktop: Ensure Windows speech voices are installed when running locally
- On Render/Railway: cloud TTS may not be available; use pre-generated mp3 with `st.audio()` or handle gracefully in code

**Model download fails:**
- Check internet connection
- Verify HuggingFace token is correct
- Try again (may take time on slow connections)

**Camera not working:**
- Grant camera permissions in browser
- Try different browser
- Check device camera settings

### Performance Tips

- **Close other apps** when running analysis
- **Use clear, well-lit photos** for best results
- **Restart app** if it becomes slow
- **Clear browser cache** if interface issues occur

## 📈 Model Information

- **Framework**: TensorFlow/Keras
- **Architecture**: Convolutional Neural Network (CNN)
- **Input**: 256x256 RGB images
- **Output**: 5-class classification
- **Accuracy**: ~95% on test dataset
- **Size**: ~50MB (downloads automatically)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Tomato disease dataset from PlantVillage
- TensorFlow/Keras for ML framework
- Streamlit for web interface
- HuggingFace for model hosting

---

**Made with ❤️ for farmers and gardeners worldwide**
