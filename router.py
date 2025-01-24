from semantic_router import Route, RouteLayer
from semantic_router.encoders import HuggingFaceEncoder
import json
with open ('query.json','r') as file:
    query_data = json.load(file)

routes = []

for category, questions in query_data.items():
    route = Route(
        name = category,
        utterances = questions
    )
    routes.append(route)

encoder = HuggingFaceEncoder()
encoder.score_threshold = 0.3

rl = RouteLayer(encoder = encoder, routes = routes)
