from input_formats.base import Base
import logging

class Text(Base):
    def loop_action(self, llm_service, pre_args, question):            
        response = llm_service.get_response(question)

        logging.info(f"Assistant:\n{response}")

