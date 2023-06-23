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


if "bot1_mesg" not in st.session_state:
    st.session_state["bot1_mesg"] = []

if "bot2_mesg" not in st.session_state:
    st.session_state["bot2_mesg"] = []

if 'batch_flag' not in st.session_state:
    st.session_state["batch_flag"] = False

if 'translate_flag' not in st.session_state:
    st.session_state["translate_flag"] = False

if 'audio_flag' not in st.session_state:
    st.session_state["audio_flag"] = False


def show_messages(mesg1_list, mesg2_list, container,
                  time_delay, batch=False, audio=False,
                  translation=False):
    """Display conversation exchanges. This helper function supports
    displaying original texts, translated texts, and audio speech. Only
    call this helper function when all the conversation exchange has been
    generated and recorded in the session states.

    Args:
    --------
    mesg1_list: list of messages spoken by the first bot
    mesg2_list: list of messages spoken by the second bot
    container: placeholder for display conversations
    time_delay: time interval between conversations
    batch: True/False to indicate if conversations will be shown
           all together or with a certain time delay.
    audio: True/False to indicate if the audio speech need to
           be appended to the texts  
    translation: True/False to indicate if the translated texts need to
                 be displayed     
    """    

    with container:
        for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
            for i, mesg in enumerate([mesg_1, mesg_2]):
                # Show original exchange ()
                message(f"{mesg['content']}", is_user=i==1, avatar_style="bottts", 
                        seed=AVATAR_SEED[i],
                        key=f"message_{i}_{mesg['role']}_{mesg['content']}")
                
                # Mimic time interval between conversations
                # (this time delay only appears when generating 
                # the conversation script for the first time)
                if not batch:
                    time.sleep(time_delay)

                # Show translated exchange
                if translation:
                    message(f"{mesg['translation']}", is_user=i==1, avatar_style="bottts", 
                            seed=AVATAR_SEED[i], 
                            key=f"message_{i}_{mesg['role']}_{mesg['translation']}")

                # Append autio to the exchange
                if audio:
                    tts = gTTS(text=mesg['content'], lang=AUDIO_SPEECH[language])  
                    sound_file = BytesIO()
                    tts.write_to_fp(sound_file)
                    st.audio(sound_file)