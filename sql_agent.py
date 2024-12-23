from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
import re

# Initialize the database
db = SQLDatabase.from_uri("sqlite:///database.db")

# Initialize the LLM
llm = OllamaLLM(model='llama3')

# Define the examples for few-shot learning
examples = [
    {
        "input": "Show the top 5 foods with the highest energy content.",
        "query": 'SELECT "Main food description", "Energy (kcal)" FROM "database" ORDER BY CAST("Energy (kcal)" AS FLOAT) DESC LIMIT 5;'
    },
    {
        "input": "List foods that have more than 10 grams of protein and less than 20 grams of carbohydrates.",
        "query": 'SELECT "Main food description", "Protein (g)", "Carbohydrate (g)" FROM "database" WHERE CAST("Protein (g)" AS FLOAT) > 10 AND CAST("Carbohydrate (g)" AS FLOAT) < 20;'
    },
    {
        "input": "Find the energy, protein, and fat content of chicken breast.",
        "query": 'SELECT "Main food description", "Energy (kcal)", "Protein (g)", "Total Fat (g)" FROM "database" WHERE "Main food description" LIKE \'%chicken breast%\';'
    },
    {
        "input": "Which food has the lowest fat content?",
        "query": 'SELECT "Main food description", "Total Fat (g)" FROM "database" WHERE CAST("Total Fat (g)" AS FLOAT) = (SELECT MIN(CAST("Total Fat (g)" AS FLOAT)) FROM "database");'
    },
    {
        "input": "What is the average protein content of foods that contain more than 200 kcal energy?",
        "query": 'SELECT AVG(CAST("Protein (g)" AS FLOAT)) AS "Average Protein" FROM "database" WHERE CAST("Energy (kcal)" AS FLOAT) > 200;'
    },
]

# Initialize the embedding model and semantic similarity selector
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=[{"input": ex["input"], "query": ex["query"]} for ex in examples],
    embeddings=embeddings,
    vectorstore_cls=FAISS,
    k=2
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
        # Capture and suggest improvements
        return f"Execution Error: {e}. Try modifying the query or reviewing the database schema."

# Create the query generation chain
query_writer = dynamic_few_shot_prompt | llm | StrOutputParser()

# Function to extract SQL query from LLM output
def extract_sql_query(llm_output):
    # Use a regular expression to capture the SQL query block
    match = re.search(r"(SELECT.*?;)", llm_output, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()  # Return the SQL query only
    return None

# Define the complete chain
def full_chain(question):
    # Generate the SQL query
    llm_output = query_writer.invoke({"question": question})
    
    # Extract the SQL query
    sql_query = extract_sql_query(llm_output)
    if not sql_query:
        return f"Error: Could not extract SQL query from LLM output.\nLLM Output: {llm_output}"
    
    # Execute the SQL query
    result = execute_sql_query(sql_query)

    # Format the response
    response = f"Question: {question}\nSQL Query: {sql_query}\nResult: {result}"
    return response

# User question
user_question = "How many protein does chicken breast have"

# Execute the chain
response = full_chain(user_question)

# Output the result
print(response)
