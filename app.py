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
