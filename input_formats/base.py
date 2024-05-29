class Base: 
    def __init__(self, console):
        self.console = console
        self.messages = {
            "loop_start": "\n[cyan]Please enter your question: Press Ctrl+C to exit.\n",
            "exiting": "\n[red]Exiting...",
            "session_ended": "[cyan]Session ended."
        }
    
    def pre_action(self):
        return {}

    def loop_action(self, llm_service, pre_args, question):
        pass

    def action(self, llm_service):
        pre_args = self.pre_action()
        try:
            while True:
                question = self.console.input(self.messages["loop_start"])
                self.loop_action(llm_service, pre_args=pre_args, question=question)

        except KeyboardInterrupt:
            self.console.print(self.messages["exiting"])

        self.console.print(self.messages["session_ended"])        