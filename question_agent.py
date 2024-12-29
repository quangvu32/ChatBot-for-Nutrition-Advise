from langchain_ollama import OllamaLLM
from rag import searcher
from sql_agent import retrieve
from langchain.schema import HumanMessage, AIMessage

llm = OllamaLLM(model="llama3")

def answer(user_query: str, chat_history: list):
    retrieve1 = searcher(user_query)  
    retrieve2 = retrieve(user_query)  

    retrieve1_text = "\n".join([f"Result {i+1}: {item}" for i, item in enumerate(retrieve1)])
    retrieve2_text = "\n".join([f"Result {i+1}: {item}" for i, item in enumerate(retrieve2)])

    history_str = "\n".join([f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}" for message in chat_history])

    system_prompt = f"""
    You are an intelligent agent tasked with providing helpful responses based on the information provided. If you 
    find the information not useful for the question then ignore it
    Given the retrieved data, the user's query, and the chat history, provide an accurate and relevant response.

    Retrieved Information (from wikipedia):
    {retrieve1_text}

    Retrieved Information (from database):
    {retrieve2_text}

    Chat History:
    {history_str}

    User's Query:
    {user_query}
    """

    message = [HumanMessage(content=system_prompt)]

    ai_response = llm.invoke(message)

    return ai_response

