from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-6')

def reranking(ingredient, search_results):
    food_scores = []
    for food_name in search_results: 
        input_pair = [ingredient, food_name]
        score = model.predict([input_pair])[0]  
        food_scores.append((food_name, score))
    food_scores.sort(key=lambda x: x[1], reverse=True)
    return food_scores[0][0] if food_scores else None  # Return the top food name