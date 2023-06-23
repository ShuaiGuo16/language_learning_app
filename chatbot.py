# Content: Class definition of interactive chatbot system 
# Author: Shuai Guo
# Email: shuaiguo0916@hotmail.com
# Date: June, 2023

import os
import openai
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


class Chatbot:
    """Class definition for a single chatbot with memory, created with LangChain."""
    
    def __init__(self, engine):
        """Select backbone large language model, as well as instantiate 
        the memory for creating language chain in LangChain.
        
        Parameters:
        --------------
        
        engine: the backbone llm-based chat model.
                "OpenAI" stands for OpenAI chat model;
                Other chat models are also possible in LangChain, 
                see https://python.langchain.com/en/latest/modules/models/chat/integrations.html
        """
        
        # Instantiate llm
        if engine == 'OpenAI':
            # Reminder: need to set up openAI API key 
            # (e.g., via environment variable OPENAI_API_KEY)
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )


        else:
            raise KeyError("Currently unsupported chat model type!")
        
        # Instantiate memory
        self.memory = ConversationBufferMemory(return_messages=True)