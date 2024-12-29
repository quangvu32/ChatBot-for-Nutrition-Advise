from semantic_router import Route, RouteLayer
from semantic_router.encoders import HuggingFaceEncoder

chit_chat = Route(
    name='small_talk',
    utterances=[
        "How's the weather today?",
        "Tell me a fun fact!",
        "What's your favorite food?",
        "Do you like talking to people?",
        "How can I make my day better?"
    ]
)

diet_tracker = Route(
    name='diet_tracker',
    utterances=[
        "I had a salad for lunch today.",
        "Can you add three bananas to my diet log?",
        "How many calories have I consumed today?",
        "Track my dinner: grilled chicken and veggies.",
        "What’s my progress this week?"
    ]
)

nutrition_advise = Route(
    name='nutrition_advisor',
    utterances=[
        "What are some good sources of protein?",
        "Should I eat more carbs if I work out regularly?",
        "Can you suggest a healthy breakfast option?",
        "Is avocado a good choice for a snack?",
        "What vitamins should I take daily?"
    ]
)

routes = [chit_chat, diet_tracker, nutrition_advise]

encoder = HuggingFaceEncoder()
encoder.score_threshold = 0.3

rl = RouteLayer(encoder = encoder, routes = routes)
'''
def router(query : str):
    print(">Router")
    route = rl(query)
    if route.name == 'small_talk':
        return small_talker(query)
    if route.name == 'diet_tracker':
        return 'init_user_db'
    if route.name == 'nutrition_advisor':
        return 'sql_agent'
    return "Sorry I couldn't answer your request"


#print(router('hello how are you'))
'''