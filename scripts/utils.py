from PIL import Image
import streamlit as st
import numpy as np
import tensorflow as tf
import os



from io import BytesIO
from huggingface_hub import hf_hub_download


#base_path = os.path.dirname(__file__)
#model_path  = os.path.join(base_path,"botaniq_model.keras")

REPO_ID = "PAMify001/BotanIQ_Model"
FILENAME = "botaniq_model.keras"


# Voice functions for TTS - tries pyttsx3 first, falls back to Windows System.Speech
import os
import subprocess
import tempfile

# Try to import pyttsx3, but don't fail if not available
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

def get_available_voices():
    """Get available voices, preferring pyttsx3 if available"""
    if PYTTSX3_AVAILABLE:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices:
                return [voice.name for voice in voices]
        except Exception as e:
            print(f"pyttsx3 voice enumeration failed: {e}")

    # Fallback to Windows System.Speech
    try:
        cmd = [
            "powershell",
            "-Command",
            (
                "Add-Type -AssemblyName System.Speech; "
                "$s=(New-Object System.Speech.Synthesis.SpeechSynthesizer); "
                "$s.GetInstalledVoices() | ForEach-Object {$_.VoiceInfo.Name}"
            ),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        voices = [v.strip() for v in proc.stdout.splitlines() if v.strip()]
        if voices:
            return voices
    except Exception as e:
        print(f"Windows voice enumeration failed: {e}")

    return ["Default Voice"]

def speak_text_with_settings(text, voice_index=0, rate=180, volume=0.8):
    """Speak text using best available TTS method"""
    # Try pyttsx3 first if available
    if PYTTSX3_AVAILABLE:
        try:
            engine = pyttsx3.init()

            # Set voice
            voices = engine.getProperty('voices')
            if voices and voice_index < len(voices):
                engine.setProperty('voice', voices[voice_index].id)

            # Set rate and volume
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)

            # Speak and wait
            engine.say(text)
            engine.runAndWait()
            print("✅ TTS: pyttsx3 used successfully")
            return None  # No file created
        except Exception as e:
            print(f"pyttsx3 failed, trying Windows fallback: {e}")

    # Fallback to Windows System.Speech (creates WAV file)
    try:
        # rate is already Windows-style (-10..10); volume is 0-100 percent
        win_rate = max(-10, min(10, rate))
        win_volume = max(0, min(100, volume))

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_path = tmp.name
        tmp.close()

        safe_text = text.replace("'", "''")
        safe_path = tmp_path.replace("'", "''")

        ps = (
            "Add-Type -AssemblyName System.Speech;"
            "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "$voices = $synth.GetInstalledVoices();"
            f"if ($voices.Count -gt {voice_index}) {{ $synth.SelectVoice($voices[{voice_index}].VoiceInfo.Name) }};"
            f"$synth.Rate = {win_rate};"
            f"$synth.Volume = {win_volume};"
            "$synth.SetOutputToWaveFile('" + safe_path + "');"
            "$synth.Speak('" + safe_text + "');"
            "$synth.Dispose();"
        )

        subprocess.run(["powershell", "-Command", ps], check=True)

        print(f"✅ TTS audio generated: {tmp_path}")
        return tmp_path

    except Exception as e:
        print(f"All TTS methods failed: {e}")
        print(f"🎤 Text: {text}")
        return None

# this the utilities where functions that help the main streamlit interface work

#path = "C:\\Users\\DELL\\Documents\\levels.png"

# this function opens and loads the image from the user devices and passes it to the  resize and rescale function for preprocessing
def load_image(path):

    try:
        img = Image.open(path)
        print("image opened successfully")
        return img
        
    except IOError:
        print("An error occurred while trying to load image")
    except Exception as e:
        print(f"Something unexpected happened while trying to open image {e}")
        

# this function resizes and rescales the input image from the user before it is passed to the model
def resize_and_rescale(image_path,target_size=(256,256)):
    # opens the file, checks if there is any error before proceeding
    try:
        
        img = load_image(image_path)

        if img is None:
            return None
        else:
            print("not none")
        

        resized_image = img.resize(target_size)
        #st.write(resized_image.size)
        #print(resized_image.size)
        #img_array = np.array(resized_image).astype('float32') / 255.0
        img_array = np.array(resized_image).astype('float32')
        img_array_e = np.expand_dims(img_array,axis=0)
        print("array scaled successfully")

        # returns the resized and rescaled image 
        return img_array_e
        
        
    except Exception as e:
        print(f"something happened{e}")
        return None
    
    

# this function loads the model from huggingface hub
@st.cache_resource 
def load_model():
    try:
        # Try to load from local file first
        model_path = os.path.join(os.path.dirname(__file__), "..", "..", "botaniq_model.keras")
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            return model
        else:
            # Fallback to HuggingFace if local file doesn't exist
            model_path = hf_hub_download(repo_id=REPO_ID,
                                          filename=FILENAME,
                                          token=st.secrets["HF_TOKEN"])
            model = tf.keras.models.load_model(model_path)
            return model
    except Exception as e:
        # If all else fails, try to load from HuggingFace without token (if public)
        try:
            model_path = hf_hub_download(repo_id=REPO_ID,
                                          filename=FILENAME)
            model = tf.keras.models.load_model(model_path)
            return model
        except:
            raise Exception(f"Could not load model: {str(e)}") 

#local_model = tf.keras.models.load_model(model_path) # the local model path
# model = load_model() # the huggingface model path - removed to avoid loading at import time

# this function is for predicting the disease 
def predict_disease(image):
    model = load_model()

    #local_model = tf.keras.models.load_model(model_path) # this loads the trained model


    image_to_predict = resize_and_rescale(image) # this preprocesses the image
    #print(image_to_predict)
    # making prediction - checks if the image preprocessing was successful
    if image_to_predict is not None:
        prediction = model.predict(image_to_predict) # this makes the prediction
        #prediction = local_model.predict(image_to_predict) # this makes the prediction
        print(prediction)

        # this returns the prediction made by the model
        return prediction
        
        
    else:
        print("image processing failed")
        return 'prediction not made because image processing failed..'
    




# this function gives our model its voice
# this uses the pyttsx3 library to convert text to speech
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
# this function combines the prediction  and voice feature together
def say_disease(disease_index):

    disease_dict = { 
        0: "Tomato Bacterial Spot",
        1: "Tomato Early Blight",
        2: "Tomato Late Blight",
        3: "Tomato Septoria Leaf Spot",
        4: "Healthy Tomato"      
              }

    disease_dict = { 
        0: "Tomato Bacterial Spot",
        1: "Tomato Early Blight",
        2: "Tomato Late Blight",
        3: "Tomato Septoria Leaf Spot",
        4: "Healthy Tomato"      
              }
    
    disease_description = {
        0: "Bacterial spot is a common disease in tomatoes caused by the bacterium Xanthomonas campestris pv. vesicatoria. It grows in warm, wet weather and spreads through water splashes, dirty tools, and bad seeds. You will see small wet spots on leaves that grow bigger and turn dark brown or black, with yellow edges. Fruit may get rough, scabby marks. To fix it, use good seeds, change where you plant tomatoes each year, and spray with copper-based chemicals to prevent it.",
        1: "Early blight is a fungus disease in tomatoes caused by Alternaria solani. It likes warm, damp weather and spreads through old plant parts, soil, and water splashes. You see rings on old leaves, making them yellow and fall off. Fruit may get dark, sunken spots. To manage it, change planting spots each year, remove old plant parts, and spray with fungicides like chlorothalonil or copper products.",
        2: "Late blight is a bad disease in tomatoes caused by the oomycete Phytophthora infestans. It grows in cool, wet weather and spreads fast through air and water. You see dark wet spots on leaves, stems, and fruit, with white growth under leaves. Fruit may rot fully. To control it, use good seeds, change planting spots, and spray fungicides like chlorothalonil or copper products to prevent it.",
        3: "Septoria leaf spot is a fungus disease in tomatoes caused by Septoria lycopersici. It grows in warm, damp weather and spreads through water splashes and old plant parts. You see many small round spots with dark edges and light centers, with tiny black dots inside. To manage it, cut off and burn all bad leaves right away, and make air flow better by tying up plants. Use fungicides like Mancozeb or Potassium Bicarbonate if needed.",
        4: "A healthy tomato plant has bright green leaves, strong stems, and lots of fruit. Leaves should have no spots, color changes, or wilting, showing no diseases or lack of food. The plant should have good roots and grow steadily without bugs. Water regularly, feed properly, and give enough sunlight to keep it healthy." }
    
    disease_name = disease_dict.get(disease_index, "Unknown Disease")

    # this is a conditional to check the model prediction and return the appropriate response
    voice_settings = st.session_state.get('voice_settings', {'voice_index': 0, 'speed': 0, 'volume': 100})

    if disease_dict.get(disease_index) == "Tomato Bacterial Spot":
        text_description = disease_description.get(disease_index)
        text_to_speak = f"The detected disease is {disease_name}, {text_description}"
        audio_path = speak_text_with_settings(
            text_to_speak,
            voice_settings['voice_index'],
            voice_settings['speed'],
            int(voice_settings['volume']),
        )
        return text_to_speak, audio_path

    elif disease_dict.get(disease_index) == "Tomato Early Blight":
        text_description = disease_description.get(disease_index)
        text_to_speak = f"The detected disease is {disease_name}, {text_description}"  
        audio_path = speak_text_with_settings(
            text_to_speak,
            voice_settings['voice_index'],
            voice_settings['speed'],
            int(voice_settings['volume']),
        )
        return text_to_speak, audio_path

    elif disease_dict.get(disease_index) == "Tomato Late Blight":
        text_description = disease_description.get(disease_index)
        text_to_speak = f"The detected disease is {disease_name}, {text_description}"
        audio_path = speak_text_with_settings(
            text_to_speak,
            voice_settings['voice_index'],
            voice_settings['speed'],
            int(voice_settings['volume']),
        )
        return text_to_speak, audio_path

    elif disease_dict.get(disease_index) == "Tomato Septoria Leaf Spot":
        text_description = disease_description.get(disease_index)
        text_to_speak = f"The detected disease is {disease_name}, {text_description}"
        audio_path = speak_text_with_settings(
            text_to_speak,
            voice_settings['voice_index'],
            voice_settings['speed'],
            int(voice_settings['volume']),
        )
        return text_to_speak, audio_path

    elif disease_dict.get(disease_index) == "Healthy Tomato":
        text_description = disease_description.get(disease_index)
        text_to_speak = f"The plant is healthy with no disease found. {text_description}"
        audio_path = speak_text_with_settings(
            text_to_speak,
            voice_settings['voice_index'],
            voice_settings['speed'],
            int(voice_settings['volume']),
        )
        return text_to_speak, audio_path
    else:
        text_description = "Unknown disease detected. Please try another image."
        text_to_speak = f"The detected disease is unknown. {text_description}"
        audio_path = speak_text_with_settings(
            text_to_speak,
            voice_settings['voice_index'],
            voice_settings['speed'],
            int(voice_settings['volume']),
        )
        return text_to_speak, audio_path
    



    


def main():
    # Test code commented out as model is no longer globally loaded
    # imag = "C:\\Users\\DELL\\Documents\\Plant_Model\\dataset\\train\\Tomato_late_blight\\0a39aa48-3f94-4696-9e43-ff4a93529dc3___RS_Late.B 5103.JPG"
    # image_path_ = "C:\\Users\\DELL\\Documents\\Plant_Model\\dataset\\train\\Tomato_late_blight\\0a4b3cde-c83a-4c83-b037-010369738152___RS_Late.B 6985.JPG"
    # tomato_spot = "C:\\Users\\DELL\\Documents\\Plant_Model\\dataset\\train\\Tomato_septoria_spot\\0a5edec2-e297-4a25-86fc-78f03772c100___JR_Sept.L.S 8468_180deg.JPG"
    # print(model.summary())
    # print(predict_disease(tomato_spot))
    # say_disease(predict_disease(tomato_spot)[0],audio_file="audio.mp3")
    pass

"""
# Testing model's actual performance with real image uploads
def predict_tomato_disease(image_path):
    img = keras.preprocessing.image.load_img(image_path, target_size=IMG_SIZE)
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    model_v =  tf.keras.models.load_model("botaniq_model.keras")
    predictions = model_v.predict(img_array, verbose=0)
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0])

    print(f"Predicted Disease: {class_names[predicted_class]}")
    print(f"Confidence: {confidence:.2%}")
    print("All probabilities:")

    for i, (name, prob) in enumerate(zip(class_names, predictions[0])):
        print(f"{i+1}. {name}: {prob:.2%}")

    return class_names[predicted_class]


#from google.colab import files
uploaded = files.upload()

for filename in uploaded.keys():
    prediction = predict_tomato_disease(filename)
    print(f"{filename}: {prediction}")
"""
if __name__ == "__main__":
    main()
