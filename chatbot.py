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



    def instruct(self, role, oppo_role, language, scenario, 
                 session_length, proficiency_level, 
                 learning_mode, starter=False):
        """Determine the context of chatbot interaction. 
        
        Parameters:
        -----------
        
        role: the role played by the current bot. 
        oppo_role: the role played by the opponent bot.
        language: the language the conversation/debate will be conducted. This is 
                  the target language the user is trying to learn.
        scenario: for conversation, scenario represents the place where the conversation 
                  is happening; for debate, scenario represents the debating topic.
        session_length: the number of exchanges between two chatbots. Two levels are possible:
                        "Short" or "Long".
        proficiency_level: assumed user's proficiency level in target language. This 
                           provides the guideline for the chatbots in terms of the 
                           language complexity they will use. Three levels are possible:
                           "Beginner", "Intermediate", and "Advanced".
        learning_mode: two modes are possible for language learning purposes:
                       "Conversation" --> where two bots are chatting in a specified scenario;
                       "Debate" --> where two bots are debating on a specified topic.
        starter: flag to indicate if the current chatbot should lead the talking.
        """

        # Define language settings
        self.role = role
        self.oppo_role = oppo_role
        self.language = language
        self.scenario = scenario
        self.session_length = session_length
        self.proficiency_level = proficiency_level
        self.learning_mode = learning_mode
        self.starter = starter
        
        # Define prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self._specify_system_message()),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("""{input}""")
        ])
        
        # Create conversation chain
        self.conversation = ConversationChain(memory=self.memory, prompt=prompt, 
                                              llm=self.llm, verbose=False)