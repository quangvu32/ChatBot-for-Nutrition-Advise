import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from router import rl
from question_agent import answer
from small_talk_agent import small_talker
from user_data_tool import init_user_db, view_diet, search_nutrition, insert_user_data
from query_agent import extract_food_with_llm
from unitconverter import convert_to_grams
from cross_encoder import reranking
init_user_db()
chat_history = []

def router(query: str):
    print(">Router")
    route = rl(query)
    
    if route.name == 'small_talk':
        print("small talking")
        response = small_talker(query, chat_history)
    
    elif route.name == 'diet_tracker':
        print("diet tracking")
        parse_results = extract_food_with_llm(query,chat_history) #Parse results: [{'food': 'apples', 'amount': '100 grams'}]
        print(f"Parse results: {parse_results}")
        g_parse_results = convert_to_grams(parse_results) #Parse results with right unit : [{'food': 'apples', 'amount': 100.0}]
        print(f"Parse results with right unit : {g_parse_results}")
        for result in g_parse_results:
            food_data = search_nutrition(result.get('food'))
            if len(food_data) == 0:
                return "Sorry I couldn't find your food in our database"
            elif len(food_data) == 1:
                insert_user_data(food_data,result['amount'])
            else:
                ori_name = result.get('food')
                food_names = [entry[0] for entry in food_data]  
                final = reranking(ori_name, food_names)
                print("ori_names :", ori_name)
                print("food_names :",food_names)
                print("final:", final, "type:", type(final))
                print("food_data:", food_data, "type:", type(food_data))
                for food in food_data :
                    if food[0] == final:
                        fin = food
                        print("found it")
                        break
                insert_user_data(fin,result['amount'])
        response = "Saving complete"
        data = view_diet()
        if data:
            st.write("Here is the list of diet reports:")
            st.dataframe(data)
        else:
            st.write("No data available or error in fetching data.")

    
    elif route.name == 'nutrition_advisor':
        response = answer(query, chat_history)
    
    else:
        response = "Sorry, I couldn't answer your request"
    
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response))
    
    return response

st.title("Nutrition Advisor Chatbot")
for message in chat_history:
    if isinstance(message, HumanMessage):
        st.markdown(f"**You:** {message.content}")
    elif isinstance(message, AIMessage):
        st.markdown(f"**Bot:** {message.content}")

user_input = st.text_input("Ask me anything about nutrition:")

if user_input:
    response = router(user_input)
    
    st.markdown(f"**Bot:** {response}")

    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response))

if st.button("Clear Chat"):
    chat_history.clear()
