from langchain_ollama import OllamaLLM
from rag import searcher
from sql_agent import retrieve
from langchain.schema import HumanMessage, AIMessage
import time
llm = OllamaLLM(model="llama3")


def answer(user_query: str, chat_history: list):
    retrieve1 = searcher(user_query)
    start_time1 = time.time()
    retrieve2 = retrieve(user_query)
    print("--- %s sql agent ---" % (time.time() - start_time1))

    with open('rag_results.txt', 'w') as f:
        f.write(str(retrieve1))
    with open('sql_agent_results.txt', 'w') as f:
        f.write(str(retrieve2))
    
    retrieve1_text = "\n".join([f"Result {i+1}: {item}" for i, item in enumerate(retrieve1)])
    retrieve2_text = "\n".join([f"Result {i+1}: {item}" for i, item in enumerate(retrieve2)])

    if len(chat_history) > 6:  
        chat_history = chat_history[-6:]

    history_str = "\n".join([
        f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}" 
        for message in chat_history
    ])
    print(history_str)
    system_prompt = f"""
    You are an intelligent agent tasked with providing helpful responses based on the information provided. 
    If you find the information not useful for the question, then ignore it.
    
    Given the retrieved data, the user's query, and the chat history, provide an accurate and relevant response.

    Retrieved Information (from Wikipedia):
    {retrieve1_text}

    Retrieved Information (from Database):
    {retrieve2_text}

    Chat History:
    {history_str}

    User's Query:
    {user_query}

    Remember to answer the question short and to the point
    """

    message = [HumanMessage(content=system_prompt)]
    start_time = time.time()
    ai_response = llm.invoke(message)

    chat_history.append(HumanMessage(content=user_query))
    chat_history.append(AIMessage(content=ai_response if isinstance(ai_response, str) else str(ai_response)))
    print("--- %s question answering agent ---" % (time.time() - start_time))
    return ai_response
