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

if 'message_counter' not in st.session_state:
    st.session_state["message_counter"] = 0


def show_messages(mesg_1, mesg_2, message_counter,
                  time_delay, batch=False, audio=False,
                  translation=False):
    """Display conversation exchanges. This helper function supports
    displaying original texts, translated texts, and audio speech. 

    Args:
    --------
    mesg1: messages spoken by the first bot
    mesg2: messages spoken by the second bot
    message_counter: create unique ID key for chat messages
    time_delay: time interval between conversations
    batch: True/False to indicate if conversations will be shown
           all together or with a certain time delay.
    audio: True/False to indicate if the audio speech need to
           be appended to the texts  
    translation: True/False to indicate if the translated texts need to
                 be displayed    

    Output:
    -------
    message_counter: updated counter for ID key
    """    

    for i, mesg in enumerate([mesg_1, mesg_2]):
        # Show original exchange ()
        message(f"{mesg['content']}", is_user=i==1, avatar_style="bottts", 
                seed=AVATAR_SEED[i],
                key=message_counter)
        message_counter += 1
        
        # Mimic time interval between conversations
        # (this time delay only appears when generating 
        # the conversation script for the first time)
        if not batch:
            time.sleep(time_delay)

        # Show translated exchange
        if translation:
            message(f"{mesg['translation']}", is_user=i==1, avatar_style="bottts", 
                    seed=AVATAR_SEED[i], 
                    key=message_counter)
            message_counter += 1

        # Append autio to the exchange
        if audio:
            tts = gTTS(text=mesg['content'], lang=AUDIO_SPEECH[language])  
            sound_file = BytesIO()
            tts.write_to_fp(sound_file)
            st.audio(sound_file)

    return message_counter


# Define the button layout at the beginning
translate_col, original_col, audio_col = st.columns(3)

# Create the conversation container
conversation_container = st.container()

if 'dual_chatbots' not in st.session_state:

    if st.sidebar.button('Generate'):

        # Add flag to indicate if this is the first time running the script
        st.session_state["first_time_exec"] = True 

        with conversation_container:
            if learning_mode == 'Conversation':
                st.write(f"""#### The following conversation happens between 
                                {role1} and {role2} {scenario} 🎭""")

            else:
                st.write(f"""#### Debate 💬: {scenario}""")

            # Instantiate dual-chatbot system
            dual_chatbots = DualChatbot(engine, role_dict, language, scenario, 
                                        proficiency_level, learning_mode, session_length)
            st.session_state['dual_chatbots'] = dual_chatbots
            
            # Start exchanges
            for _ in range(MAX_EXCHANGE_COUNTS[session_length][learning_mode]):
                output1, output2, translate1, translate2 = dual_chatbots.step()

                mesg_1 = {"role": dual_chatbots.chatbots['role1']['name'], 
                        "content": output1, "translation": translate1}
                mesg_2 = {"role": dual_chatbots.chatbots['role2']['name'], 
                        "content": output2, "translation": translate2}
                
                new_count = show_messages(mesg_1, mesg_2, 
                                          st.session_state["message_counter"],
                                          time_delay=time_delay, batch=False,
                                          audio=False, translation=False)
                st.session_state["message_counter"] = new_count

                # Update session state
                st.session_state.bot1_mesg.append(mesg_1)
                st.session_state.bot2_mesg.append(mesg_2)
                


if 'dual_chatbots' in st.session_state:  

    # Show translation 
    if translate_col.button('Translate to English'):
        st.session_state['translate_flag'] = True
        st.session_state['batch_flag'] = True

    # Show original text
    if original_col.button('Show original'):
        st.session_state['translate_flag'] = False
        st.session_state['batch_flag'] = True

    # Append audio
    if audio_col.button('Play audio'):
        st.session_state['audio_flag'] = True
        st.session_state['batch_flag'] = True

    # Retrieve generated conversation & chatbots
    mesg1_list = st.session_state.bot1_mesg
    mesg2_list = st.session_state.bot2_mesg
    dual_chatbots = st.session_state['dual_chatbots']
    
    # Control message appear
    if st.session_state["first_time_exec"]:
        st.session_state['first_time_exec'] = False
    
    else:
        # Show complete message
        with conversation_container:
            
            if learning_mode == 'Conversation':
                st.write(f"""#### {role1} and {role2} {scenario} 🎭""")

            else:
                st.write(f"""#### Debate 💬: {scenario}""")
        
            for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
                new_count = show_messages(mesg_1, mesg_2, 
                                        st.session_state["message_counter"],
                                        time_delay=time_delay,
                                        batch=st.session_state['batch_flag'],
                                        audio=st.session_state['audio_flag'],
                                        translation=st.session_state['translate_flag'])
                st.session_state["message_counter"] = new_count
    

    # Create summary for key learning points
    summary_expander = st.expander('Key Learning Points')
    scripts = []
    for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
        for i, mesg in enumerate([mesg_1, mesg_2]):
            scripts.append(mesg['role'] + ': ' + mesg['content'])
    
    # Compile summary
    if "summary" not in st.session_state:
        summary = dual_chatbots.summary(scripts)
        st.session_state["summary"] = summary
    else:
        summary = st.session_state["summary"]
    
    with summary_expander:
        st.markdown(f"**Here is the learning summary:**")
        st.write(summary)