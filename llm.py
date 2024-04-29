from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

class LllService:
    def __init__(self, config: dict, verbose: bool=False) -> None:
      template_text = config["template"]
      prompt = PromptTemplate(input_variables=["history", "input"], template=template_text)  
      self.chain = ConversationChain(
        prompt=prompt,
        memory=ConversationBufferMemory(ai_prefix="Assistant:"),
        verbose=verbose,
        llm=Ollama(),
      )  

    def get_response(self, text: str) -> str:
        """Generates a response to the given text using the Llama-2 language model."""
        response = self.chain.predict(input=text)
    
        if response.startswith("Assistant:"):
            response = response[len("Assistant:") :].strip()
        return response