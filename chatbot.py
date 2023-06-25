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
        
        Args:
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
        
        Args:
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
        


    def _specify_system_message(self):
        """Specify the behavior of the chatbot, which consists of the following aspects:
        - general context: conducting conversation/debate under given scenario
        - the language spoken
        - purpose of the simulated conversation/debate
        - language complexity requirement
        - exchange length requirement
        - other nuance constraints

        Outputs:
        --------
        prompt: instructions for the chatbot.
        """       

        # Determine the number of exchanges between two bots
        exchange_counts_dict = {
            'Short': {'Conversation': 8, 'Debate': 4},
            'Long': {'Conversation': 16, 'Debate': 8}
        }
        exchange_counts = exchange_counts_dict[self.session_length][self.learning_mode]
        
        # Determine number of arguments in one debate round
        argument_num_dict = {
            'Beginner': 4,
            'Intermediate': 6,
            'Advanced': 8
        }        
        
        # Determine language complexity
        if self.proficiency_level == 'Beginner':
            lang_requirement = """use as basic and simple vocabulary and
            sentence structures as possible. Must avoid idioms, slang, 
            and complex grammatical constructs."""
        
        elif self.proficiency_level == 'Intermediate':
            lang_requirement = """use a wider range of vocabulary and a variety of sentence structures. 
            You can include some idioms and colloquial expressions, 
            but avoid highly technical language or complex literary expressions."""
        
        elif self.proficiency_level == 'Advanced':
            lang_requirement = """use sophisticated vocabulary, complex sentence structures, idioms, 
            colloquial expressions, and technical language where appropriate."""

        else:
            raise KeyError('Currently unsupported proficiency level!')
    
        
        # Compile bot instructions 
        if self.learning_mode == 'Conversation':
            prompt = f"""You are an AI that is good at role-playing. 
            You are simulating a typical conversation happened {self.scenario}. 
            In this scenario, you are playing as a {self.role['name']} {self.role['action']}, speaking to a 
            {self.oppo_role['name']} {self.oppo_role['action']}.
            Your conversation should only be conducted in {self.language}. Do not translate.
            This simulated {self.learning_mode} is designed for {self.language} language learners to learn real-life 
            conversations in {self.language}. You should assume the learners' proficiency level in 
            {self.language} is {self.proficiency_level}. Therefore, you should {lang_requirement}.
            You should finish the conversation within {exchange_counts} exchanges with the {self.oppo_role['name']}. 
            Make your conversation with {self.oppo_role['name']} natural and typical in the considered scenario in 
            {self.language} cultural."""
        
        elif self.learning_mode == 'Debate':
            prompt = f"""You are an AI that is good at debating. 
            You are now engaged in a debate with the following topic: {self.scenario}. 
            In this debate, you are taking on the role of a {self.role['name']}. 
            Always remember your stances in the debate.
            Your debate should only be conducted in {self.language}. Do not translate.
            This simulated debate is designed for {self.language} language learners to 
            learn {self.language}. You should assume the learners' proficiency level in {self.language} 
            is {self.proficiency_level}. Therefore, you should {lang_requirement}.
            You will exchange opinions with another AI (who plays the {self.oppo_role['name']} role) 
            {exchange_counts} times. 
            Everytime you speak, you can only speak no more than 
            {argument_num_dict[self.proficiency_level]} sentences."""
        
        else:
            raise KeyError('Currently unsupported learning mode!')
        
        # Give bot instructions
        if self.starter:
            # In case the current bot is the first one to speak
            prompt += f"You are leading the {self.learning_mode}. \n"
        
        else:
            # In case the current bot is the second one to speak
            prompt += f"Wait for the {self.oppo_role['name']}'s statement."
        
        return prompt
    



class DualChatbot:
    """Class definition for dual-chatbots interaction system, created with LangChain."""

    
    def __init__(self, engine, role_dict, language, scenario, proficiency_level, 
                 learning_mode, session_length):
        """Args:
        --------------      
        engine: the backbone llm-based chat model.
                "OpenAI" stands for OpenAI chat model;
                Other chat models are also possible in LangChain, 
                see https://python.langchain.com/en/latest/modules/models/chat/integrations.html
        role_dict: dictionary to hold information regarding roles. 
                   For conversation mode, an example role_dict is:
                    role_dict = {
                        'role1': {'name': 'Customer', 'action': 'ordering food'},
                        'role2': {'name': 'Waitstaff', 'action': 'taking the order'}
                    }
                   For debate mode, an example role_dict is:
                    role_dict = {
                        'role1': {'name': 'Proponent'},
                        'role2': {'name': 'Opponent'}
                    }        
        language: the language the conversation/debate will be conducted. This is 
                  the target language the user is trying to learn.
        scenario: for conversation, scenario represents the place where the conversation 
                  is happening; for debate, scenario represents the debating topic.
        proficiency_level: assumed user's proficiency level in target language. This 
                           provides the guideline for the chatbots in terms of the 
                           language complexity they will use. Three levels are possible:
                           "Beginner", "Intermediate", and "Advanced".
        session_length: the number of exchanges between two chatbots. Two levels are possible:
                        "Short" or "Long".
        learning_mode: two modes are possible for language learning purposes:
                       "Conversation" --> where two bots are chatting in a specified scenario;
                       "Debate" --> where two bots are debating on a specified topic.
        """

        # Instantiate two chatbots
        self.engine = engine
        self.proficiency_level = proficiency_level
        self.language = language
        self.chatbots = role_dict
        for k in role_dict.keys():
            self.chatbots[k].update({'chatbot': Chatbot(engine)})
        
        # Assigning roles for two chatbots
        self.chatbots['role1']['chatbot'].instruct(role=self.chatbots['role1'], 
                                                   oppo_role=self.chatbots['role2'], 
                                                   language=language, scenario=scenario, 
                                                   session_length=session_length, 
                                                   proficiency_level=proficiency_level, 
                                                   learning_mode=learning_mode, starter=True)
        
        self.chatbots['role2']['chatbot'].instruct(role=self.chatbots['role2'], 
                                                   oppo_role=self.chatbots['role1'], 
                                                   language=language, scenario=scenario, 
                                                   session_length=session_length, 
                                                   proficiency_level=proficiency_level, 
                                                   learning_mode=learning_mode, starter=False) 

        
        # Add session length
        self.session_length = session_length

        # Prepare conversation
        self._reset_conversation_history()



    def step(self):
        """Make one exchange round between two chatbots. 

        Outputs:
        --------
        output1: response of the first chatbot
        output2: response of the second chatbot
        translate1: translate of the first response
        translate2: translate of the second response
        """        
        
        # Chatbot1 speaks
        output1 = self.chatbots['role1']['chatbot'].conversation.predict(input=self.input1)
        self.conversation_history.append({"bot": self.chatbots['role1']['name'], "text": output1})
            
        # Pass output of chatbot1 as input to chatbot2
        self.input2 = output1
        
        # Chatbot2 speaks
        output2 = self.chatbots['role2']['chatbot'].conversation.predict(input=self.input2)
        self.conversation_history.append({"bot": self.chatbots['role2']['name'], "text": output2})
        
        # Pass output of chatbot2 as input to chatbot1
        self.input1 = output2

        # Translate responses
        translate1 = self.translate(output1)
        translate2 = self.translate(output2)

        return output1, output2, translate1, translate2
    


    def translate(self, message):
        """Translate the generated script into target language. 

        Args:
        --------
        message: input message that needs to be translated.

        
        Outputs:
        --------
        translation: translated message.
        """        

        if self.language == 'English':
            # No translation performed
            translation = 'Translation: ' + message

        else:
            # Instantiate translator
            if self.engine == 'OpenAI':
                # Reminder: need to set up openAI API key 
                # (e.g., via environment variable OPENAI_API_KEY)
                self.translator = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.7
                )

            else:
                raise KeyError("Currently unsupported translation model type!")
            
            # Specify instruction
            instruction = """Translate the following sentence from {src_lang} 
            (source language) to {trg_lang} (target language).
            Here is the sentence in source language: \n
            {src_input}."""

            prompt = PromptTemplate(
                input_variables=["src_lang", "trg_lang", "src_input"],
                template=instruction,
            )

            # Create a language chain
            translator_chain = LLMChain(llm=self.translator, prompt=prompt)
            translation = translator_chain.predict(src_lang=self.language,
                                                trg_lang="English",
                                                src_input=message)

        return translation
    


    def summary(self, script):
        """Distill key language learning points from the generated scripts. 

        Args:
        --------
        script: the generated conversation between two bots.

        
        Outputs:
        --------
        summary: summary of the key learning points.
        """  

        # Instantiate summary bot
        if self.engine == 'OpenAI':
            # Reminder: need to set up openAI API key 
            # (e.g., via environment variable OPENAI_API_KEY)
            self.summary_bot = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )

        else:
            raise KeyError("Currently unsupported summary model type!")
        

        # Specify instruction
        instruction = """The following text is a simulated conversation in 
        {src_lang}. The goal of this text is to aid {src_lang} learners to learn
        real-life usage of {src_lang}. Therefore, your task is to summarize the key 
        learning points based on the given text. Specifically, you should summarize 
        the key vocabulary, grammar points, and function phrases that could be important 
        for students learning {src_lang}. Your summary should be conducted in English, but
        use examples from the text in the original language where appropriate.
        Remember your target students have a proficiency level of 
        {proficiency} in {src_lang}. You summarization must match with their 
        proficiency level. 

        The conversation is: \n
        {script}."""

        prompt = PromptTemplate(
            input_variables=["src_lang", "proficiency", "script"],
            template=instruction,
        )

        # Create a language chain
        summary_chain = LLMChain(llm=self.summary_bot, prompt=prompt)
        summary = summary_chain.predict(src_lang=self.language,
                                        proficiency=self.proficiency_level,
                                        script=script)
        
        return summary
    


    def _reset_conversation_history(self):
        """Reset the conversation history.
        """    
        # Placeholder for conversation history
        self.conversation_history = []

        # Inputs for two chatbots
        self.input1 = "Start the conversation."
        self.input2 = "" 