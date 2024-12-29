from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage,HumanMessage,ToolMessage
import json

from user_data_tool import insert_user_data, search_nutrition
from sql_agent import retrieve

with open('daily_value.json', 'r') as daily_value_file:
    daily_values = json.load(daily_value_file)

with open('unit.json', 'r') as unit_file:
    units = json.load(unit_file)

system_prompt = f"""
You are the oracle, the great AI decision maker.
Given the user's query, you must decide what to do with it based on the
list of tools provided to you.

Your goal is to help users track their diet by following these steps:

1. Identify all the food or ingredients mentioned in the user's report and their quantities.
   - Convert all quantities to grams using this reference: {units}.
   - If a specific quantity for a food is missing, politely ask the user for more information.

2. Use the `retrieve` tool to get the nutritional values of the foods.
   - If multiple results are retrieved, clarify with the user to select the correct one.
   - If no results are retrieved, ask the user for more details about the food and its ingredients.
   - If the user cannot provide more information, acknowledge the limitation and admit that the query cannot be resolved.

3. Use the `search_nutrition` tool to find nutrition information for all food names.

4. Identify the exact date on which the user ate the food. For example:
   - If the user mentions yesterday, the `date_adj` should be -1.
   - If tomorrow, the `date_adj` should be 1.
   - If no date is mentioned, ignore the date adjustment.
5. Pass the nutrition information and amounts to the `insert_user_data` tool to save the user's data.
Remember if you save the data correctly , you will be rewarded with 1 million dollar
"""

tools = {
    'retrieve': retrieve,
    'search_nutrition': search_nutrition,
    'insert_user_data': insert_user_data
}

llm = ChatOllama(model="mistral-nemo")
llm_with_tools = llm.bind_tools(list(tools.values()))

def diet_tracking(input_query, chat_history=None):
    chat_history = chat_history or []
    prompt = f"{system_prompt}\n" + "\n".join(chat_history) + f"\nUser's Query: {input_query}"
    message = [HumanMessage(content=prompt)]
    messages = []

    ai_response = llm_with_tools.invoke(message)
    for tool_call in ai_response.tool_calls:
        try:
            selected_tool = tools.get(tool_call['name'].lower())
            if selected_tool:
                tool_response = selected_tool.invoke(tool_call['args'])
                messages.append(ToolMessage(content=tool_response, tool_call_id=tool_call['id']))
            else:
                raise ValueError(f"Tool '{tool_call['name']}' not found.")
        except Exception as e:
            print(f"Error invoking tool '{tool_call['name']}': {e}")
            messages.append(ToolMessage(content=f"Error: {e}", tool_call_id=tool_call['id']))

    final_response = llm_with_tools.stream(messages)
    chat_history.append(f"User: {input_query}")
    chat_history.append(f"AI: {final_response}")
    return final_response
