import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage

llm = OllamaLLM(model='llama3')

examples = """
Example Input: "I ate 200g of chicken and drank 500ml of orange juice."
Example Output: [{"food": "chicken", "amount": "200 grams"}, {"food": "orange juice", "amount": "500 milliliters"}]

Example Input: "I consumed 100g apple and 300ml pineapple juice."
Example Output: [{"food": "apple", "amount": "100 grams"}, {"food": "pineapple juice", "amount": "300 milliliters"}]

Example Input: "Yesterday, I ate 250g of broccoli and drank 400ml of milk."
Example Output: [{"food": "broccoli", "amount": "250 grams"}, {"food": "milk", "amount": "400 milliliters"}]
"""

prompt_template = PromptTemplate.from_template(
    """
You are a helpful assistant for extracting food and quantities.
Given a user's input, extract the food names and their respective amounts (including units).

Respond in JSON format as a list of dictionaries:
- "food" is the name of the food item (e.g., "apple").
- "amount" includes the quantity and unit (e.g., "200 grams").

{examples}

User Input: {user_input}
Response:
"""
)

output_parser = StrOutputParser()

def extract_food_with_llm(user_input: str, chat_history: list):
    chat_history_str = "\n".join([f"User: {message.content}" if isinstance(message, HumanMessage) else f"Bot: {message.content}" for message in chat_history])
    prompt = prompt_template.format(examples=examples, user_input=user_input)
    
    prompt_with_history = f"Chat History:\n{chat_history_str}\n{prompt}"
    
    response = llm.invoke(prompt_with_history) 
    
    match = re.search(r'(\[.*\])', response.strip(), re.DOTALL)
    if match:
        json_response = match.group(1)
        try:
            food_info = json.loads(json_response)
            return food_info
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response", "raw_response": response}, chat_history
    else:
        return {"error": "Failed to extract JSON from response", "raw_response": response}, chat_history
