from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage

# Initialize the Ollama LLM
llm = OllamaLLM(model='llama3')

# Define a conversational chain
conversation = ConversationChain(llm=llm)

def small_talker(input_text: str, chat_history: str) -> str:
    prompt = f"{input_text}\nHere are the conversation history: \n{chat_history}"
    output = conversation.invoke(prompt)
    if isinstance(output, dict) and "response" in output:
        return output["response"]
    return str(output)

