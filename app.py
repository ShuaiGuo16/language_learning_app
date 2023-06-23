# Content: Streamlit app for language learning
# Author: Shuai Guo
# Email: shuaiguo0916@hotmail.com
# Date: June, 2023

import streamlit as st
from streamlit_chat import message
from chatbot import DualChatbot
import time
from gtts import gTTS
from io import BytesIO

# Define the language learning settings
LANGUAGES = ['English', 'German', 'Spanish', 'French']
SESSION_LENGTHS = ['Short', 'Long']
PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']
MAX_EXCHANGE_COUNTS = {
    'Short': {'Conversation': 8, 'Debate': 4},
    'Long': {'Conversation': 16, 'Debate': 8}
}
AUDIO_SPEECH = {
    'English': 'en',
    'German': 'de',
    'Spanish': 'es',
    'French': 'fr'
}
AVATAR_SEED = [123, 42]

# Define backbone llm
engine = 'OpenAI'

# Set the title of the app
st.title('Language Learning App 🌍📖🎓')

# Set the description of the app
st.markdown("""
This app generates conversation or debate scripts to aid in language learning 🎯 

Choose your desired settings and press 'Generate' to start 🚀
""")

# Add a selectbox for learning mode
learning_mode = st.sidebar.selectbox('Learning Mode 📖', ('Conversation', 'Debate'))

if learning_mode == 'Conversation':
    role1 = st.sidebar.text_input('Role 1 🎭')
    action1 = st.sidebar.text_input('Action 1 🗣️')
    role2 = st.sidebar.text_input('Role 2 🎭')
    action2 = st.sidebar.text_input('Action 2 🗣️')
    scenario = st.sidebar.text_input('Scenario 🎥')
    time_delay = 2

    # Configure role dictionary
    role_dict = {
        'role1': {'name': role1, 'action': action1},
        'role2': {'name': role2, 'action': action2}
    }

else:
    scenario = st.sidebar.text_input('Debate Topic 💬')

    # Configure role dictionary
    role_dict = {
        'role1': {'name': 'Proponent'},
        'role2': {'name': 'Opponent'}
    }
    time_delay = 5

language = st.sidebar.selectbox('Target Language 🔤', LANGUAGES)
session_length = st.sidebar.selectbox('Session Length ⏰', SESSION_LENGTHS)
proficiency_level = st.sidebar.selectbox('Proficiency Level 🏆', PROFICIENCY_LEVELS)