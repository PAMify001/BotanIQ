import pyttsx3

engine = pyttsx3.init()
AI_prediction = "apple bright"
disease = {
    'name':['Your plant has apple bright, although it is not a very serious disease, it is primary caused by the plant exposure to UV radiation . To prevent this diseas , be planting apple in the right season , in season like summer when the sun is just right'],
    'cause': 'Apple bright is primarily caused, by exposure of the plant to UV radiaation ',
    'prevention': 'plant in the right season'
}

# the ai has to detect the disease, and i have to get the the disease that the ai predicted and i have to run an if else statement , if the disease is a particular disease i have to write and say a particular thing 

#engine.say("hello, how are you doing today, hope you are having a great day")
text = '''How to use them together in your Project
Here is the workflow for your "Data Collection" stage:

Define your Tools: Write small functions in utils.py to count your images or check for corrupted files.

Define your AI: Write a class in model.py that represents your specific "Plant AI."

The "Main" script: In your 02_Training.ipynb or app.py, you simply "import" these tools.

Why this helps with your crush: By using a class for the model, she can simply write my_ai = PlantClassifier('model.keras') in the Streamlit app. She doesn't need to know how the neural network layers work or how to resize the image—your class handles all that complexity "under the hood.'''
engine.say(disease['name'])
engine.runAndWait()

