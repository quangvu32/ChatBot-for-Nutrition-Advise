from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage
import time
# Initialize the Ollama LLM
llm = OllamaLLM(model='llama3')

# Define a conversational chain
conversation = ConversationChain(llm=llm)

def small_talker(input_text: str, chat_history) -> str:
    start_time = time.time()
    if len(chat_history) > 6: 
        chat_history = chat_history[-6:]
    print(chat_history)
    prompt = f"{input_text}\nHere are the conversation history: \n{chat_history}"
    output = conversation.invoke(prompt)
    print("--- %s small talk agent ---" % (time.time() - start_time))
    if isinstance(output, dict) and "response" in output:
        return output["response"]
    return str(output)
