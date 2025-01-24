from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
import re
import time

def retrieve(user_question: str):
    print("start retrieving")
    db = SQLDatabase.from_uri("sqlite:///nutrition.db")

    llm = OllamaLLM(model='llama3')

    examples = [
        {
            "input": "Show the top 5 foods with the highest energy content.",
            "query": 'SELECT "Main food", "Energy (kcal)" FROM "nutrition" ORDER BY CAST("Energy (kcal)" AS FLOAT) DESC LIMIT 5;'
        },
        {
            "input": "List foods that have more than 10 grams of protein and less than 20 grams of carbohydrates.",
            "query": 'SELECT "Main food", "Protein (g)", "Carbohydrate (g)" FROM "nutrition" WHERE CAST("Protein (g)" AS FLOAT) > 10 AND CAST("Carbohydrate (g)" AS FLOAT) < 20;'
        },
        {
            "input": "Find the energy,fiber and carbonhydrate content of brocolli.",
            "query": 'SELECT "Main food", "Energy (kcal)", "Fiber" ,"Carbohydrate (g)" FROM "nutrition" WHERE "Main food" LIKE \'%brocolli%\';'
        },
        {
            "input": "Find the energy, protein, and fat content of chicken breast.",
            "query": 'SELECT "Main food", "Energy (kcal)", "Protein (g)", "Total Fat (g)" FROM "nutrition" WHERE "Main food" LIKE \'%chicken breast%\';'
        },
        {
            "input": "Which food has the lowest fat content?",
            "query": 'SELECT "Main food", "Total Fat (g)" FROM "nutrition" WHERE CAST("Total Fat (g)" AS FLOAT) = (SELECT MIN(CAST("Total Fat (g)" AS FLOAT)) FROM "database");'
        },
        {
            "input": "What is the average protein content of foods that contain more than 200 kcal energy?",
            "query": 'SELECT AVG(CAST("Protein (g)" AS FLOAT)) AS "Average Protein" FROM "nutrition" WHERE CAST("Energy (kcal)" AS FLOAT) > 200;'
        },
        {
            "input": "List foods that are healthy",
            "query": 'SELECT "Main food", "Energy (kcal)", "Fiber, total dietary (g)", "Sugars, total\n(g)","Total Fat (g)","Protein (g)" FROM "nutrition" WHERE (CAST("Energy (kcal)" AS FLOAT) < 200) AND (CAST("Fiber, total dietary (g)" AS FLOAT) > 3) AND (CAST("Sugars, total\n(g)" AS FLOAT) < 5) AND (CAST("Total Fat (g)" AS FLOAT) < 10) AND (CAST("Protein (g)" AS FLOAT) > 5);'
        },
        {
            "input" : "List drinks that alcohol-free",
            "query" : '''SELECT "Main food", "Alcohol (g)" FROM nutrition WHERE (CAST("Alcohol (g)" AS FLOAT) = 0 OR "Alcohol (g)" IS NULL) AND "WWEIA Category" LIKE '%drink%' ORDER BY "Main food";'''
        },
        {
            "input" : "List 5 alcoholic drinks",
            "query" : 'SELECT "Main food", "Alcohol (g)" FROM nutrition WHERE "WWEIA Category" IN (\'Beer\', \'Liquor and cocktails\',\'Wine\') ORDER BY RANDOM() LIMIT 5;'
        },
        {
            "input" : 'Find foods with the highest cholesterol content',
            "query" : 'SELECT "Main food", "Cholesterol (mg)" FROM "nutrition" ORDER BY CAST("Cholesterol (mg)" AS FLOAT) DESC LIMIT 7;'
        },
        {
            "input" : "What's the nutritional value of pineapple",
            "query" : 'SELECT "Main food", "Energy (kcal)", "Protein (g)", "Total Fat (g)", "Carbohydrate (g)", "Fiber, total dietary (g)", "Sugars, total (g)" FROM "nutrition" WHERE "Main food" LIKE "%pineapple%";'
        },
        {
            "input" : "What's the nutritional value of bacon",
            "query" : 'SELECT "Main food", "Energy (kcal)", "Protein (g)", "Total Fat (g)", "Carbohydrate (g)", "Fiber, total dietary (g)", "Sugars, total (g)" FROM "nutrition" WHERE "Main food" LIKE "%bacon%";'
        },
        {
            "input": "Find the energy, protein, and fat content of 150g of pork belly.",
            "query": 'SELECT "Main food", "Energy (kcal)" * 1.5 AS "Energy (kcal)", "Protein (g)" * 1.5 AS "Protein (g)", "Total Fat (g)" * 1.5 AS "Total Fat (g)" FROM "nutrition" WHERE "Main food" LIKE \'%pork belly%\';'
        },
        {
            "input": "Find the energy, protein, and fat content of 500g of strawberries",
            "query": 'SELECT "Main food", "Energy (kcal)" * 1.5 AS "Energy (kcal)", "Protein (g)" * 1.5 AS "Protein (g)", "Total Fat (g)" * 5 AS "Total Fat (g)" FROM "nutrition" WHERE "Main food" LIKE \'%strawberry%\';'
        }   
    ]

    # Initialize the embedding model and semantic similarity selector
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples=[{"input": ex["input"], "query": ex["query"]} for ex in examples],
        embeddings=embeddings,
        vectorstore_cls=FAISS,
        k=3
    )

    # Define the dynamic few-shot prompt
    dynamic_few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template(
            "User input: {input}\nSQL query: {query}"
        ),
        input_variables=["question"],
        prefix="You are a SQL expert. Generate a valid SQL query based on the user's input.",
        suffix="User input: {question}\nSQL query:",
    )

    # Define a custom SQL executor
    def execute_sql_query(query: str):
        try:
            return db.run(query)
        except Exception as e:
            return f"Execution Error: {e}. Try modifying the query or reviewing the database schema."
        
    query_writer = dynamic_few_shot_prompt | llm | StrOutputParser()

    def extract_sql_query(llm_output):
        # Use a regular expression to capture the SQL query block
        match = re.search(r"(SELECT.*?;)", llm_output, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip() 
        return None

    def full_chain(question):
        llm_output = query_writer.invoke({"question": question})
    
        sql_query = extract_sql_query(llm_output)
        if not sql_query:
            return f"Error: Could not extract SQL query from LLM output.\nLLM Output: {llm_output}"
    
        result = execute_sql_query(sql_query)

        response = f"Question: {question}\nSQL Query: {sql_query}\nResult: {result}"
        return response
    response = full_chain(user_question)
    return response


def calculate_daily_averages_with_dates():
    db = SQLDatabase.from_uri("sqlite:///nutrition.db")
    sql_query = """
    WITH daily_totals AS (
        SELECT 
            Date,
            Nutrient,
            SUM(CAST(Value AS FLOAT)) AS DailyTotal
        FROM nutrition_data
        GROUP BY Date, Nutrient
    )
    SELECT 
        Nutrient,
        AVG(DailyTotal) AS AverageValue
    FROM daily_totals
    GROUP BY Nutrient;
    """
    try:
        result = db.run(sql_query)
    except Exception as e:
        return f"Error executing SQL query: {e}"

    response = "Average Daily Nutritional Values (Across Days):\n"
    for row in result:
        nutrient = row["Nutrient"]
        avg_value = row["AverageValue"]
        response += f"{nutrient}: {avg_value:.2f}\n"
    print('finished scanning db')
    return response
