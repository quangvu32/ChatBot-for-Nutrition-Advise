import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from router import rl
from question_agent import answer
from small_talk_agent import small_talker
from user_data_tool import init_user_db, view_diet, search_nutrition, insert_user_data
from query_agent import extract_food_with_llm
from unitconverter import convert_to_grams
from cross_encoder import reranking
import time
from delete import delete_table

init_user_db()

def router(query: str, chat_history):
    print(">Router")
    route = rl(query)
    
    if route.name == 'small_talk':
        print("small talking")
        response = small_talker(query, chat_history)
    
    elif route.name == 'diet_tracker':
        start_time = time.time()
        print("diet tracking")
        parse_results = extract_food_with_llm(query,chat_history) #Parse results: [{'food': 'apples', 'amount': '100 grams'}]
        #print(f"Parse results: {parse_results}")
        g_parse_results = convert_to_grams(parse_results) #Parse results with right unit : [{'food': 'apples', 'amount': 100.0}]
        #print(f"Parse results with right unit : {g_parse_results}")
        for result in g_parse_results:
            food_data = search_nutrition(result.get('food'))
            if len(food_data) == 0:
                print("--- %s diet_tracking ---" % (time.time() - start_time))
                return "Sorry I couldn't find your food in our database"
            elif len(food_data) == 1:
                insert_user_data(food_data,result['amount'])
            else:
                ori_name = result.get('food')
                food_names = [entry[0] for entry in food_data]  
                final = reranking(ori_name, food_names)
                #print("ori_names :", ori_name)
                #print("food_names :",food_names)
                #print("final:", final, "type:", type(final))
                #print("food_data:", food_data, "type:", type(food_data))
                for food in food_data :
                    if food[0] == final:
                        fin = food
                        break
                insert_user_data(fin,result['amount'])
        response = "Saving complete"
        print("--- %s diet_tracking ---" % (time.time() - start_time))
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
st.sidebar.title("Nutrition Advisor Chatbot")

def history(chat_history):
    for message in chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.write(message.content)
                
chat_history = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = chat_history

history(st.session_state.chat_history)

user_input = st.chat_input("Ask me anything about nutrition:")

if user_input:

    st.session_state.chat_history.append(HumanMessage(content=user_input))
    chat_history.append(HumanMessage(content=user_input))
    with st.chat_message('user'):
        st.write(user_input)

    response = router(user_input,chat_history)

    st.session_state.chat_history.append(AIMessage(content=response))
    chat_history.append(AIMessage(content=response))
    with st.chat_message('assistant'):
        full_res = ""
        holder = st.empty()

        for word in response.split():
            full_res += word + " "
            time.sleep(0.05)
            holder.markdown(full_res + "▋")
        holder.markdown(full_res) 
        
if st.sidebar.button("Clear Chat"):
    chat_history.clear()
    st.session_state.chat_history = chat_history
    history(st.session_state.chat_history)
if st.sidebar.button("Delete database"):
    delete_table()
