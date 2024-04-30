from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from vectorstore import VectorStore

class LllService:
    def __init__(self, config: dict,  verbose: bool=False) -> None:
      template = config["template"]
      
      self.prompt = PromptTemplate(
          input_variables=["context", "input"], 
          template=template
      )

      llm = Ollama(model=config["llm"]["model"], callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))   

      vectorstore = VectorStore(config);
      
      self.chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": self.prompt, "verbose":verbose},
      )


    def get_response(self, query: str) -> str:
        """Generates a response to the given text using the Llama-2 language model."""

        response = self.chain.invoke({"query": query})

        response_text = response["result"]
    
        if response_text.startswith("Assistant:"):
            response_text = response_text[len("Assistant:") :].strip()
        return response_text