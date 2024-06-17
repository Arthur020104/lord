import pandas as pd
import sys
sys.path.append('../')
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from unidecode import unidecode
from secret.apiOpenAI import api_key

# Initialize OpenAI LLM
llm = ChatOpenAI(api_key=api_key, temperature=0, model="gpt-4o")

def clear_string(input_string):
    """
    A function that removes diacritics and converts to lowercase.
    """
    return unidecode(input_string).lower()


# Prepare the prompt template for the LLM
prompt_template = """
You are a data search assistant. Your task is to generate Python code to query a DataFrame based on a user query.
Use this df = pd.read_csv("C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/ls.csv") to load the DataFrame.
You already have a function the clear_string function that removes diacritics and converts a string to lowercase.
Dont import anything else only pandas.
Use only clear_string to remove diacritics and convert to lowercase. Only apply clear_string to the user query dont over complicate the code.
Only query up to 3 items from the DataFrame never more than that.
UnitType can be only 'HOUSE', 'APARTMENT'
Never translate query names, always use the same name as the DataFrame columns.
Here is an example of the DataFrame (df):
{df_head}

The DataFrame columns are: {columns}

Always remove diacritics in comparisons both from the base and the search (before searching, remove diacritics from the database), and standardize the search without using case.

When given a user query, generate Python code that processes the DataFrame to retrieve the relevant data. The result should be stored in a variable named `result`.

User Query: {user_query}

the response must only be the python code, never return antyhing else.
Dont use  ```python or ``` at the start or finish of the code
Identation must be 4 spaces

Code Example:
"
df = pd.read_csv("C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/ls.csv")

df['UnitType'] = df['UnitType'].apply(clear_string)
df_filtered = df[
    (df['UnitType'] == clear_string(user_query['UnitType'])) &
    (df['Bedrooms'] >= user_query['Bedrooms_min']) &
    (df['Bedrooms'] <= user_query['Bedrooms_max']) &
    (df['Bathrooms'] >= user_query['Bathrooms_min']) &
    (df['Bathrooms'] <= user_query['Bathrooms_max']) &
    (df['Suites'] >= user_query['Suites_min']) &
    (df['Suites'] <= user_query['Suites_max']) &
    (df['ParkingSpaces'] >= user_query['ParkingSpaces_min']) &
    (df['ParkingSpaces'] <= user_query['ParkingSpaces_max']) &
    (df['Price'] <= user_query['Price_max'])
]
result = df_filtered.head(3)
"
"""

# Create a LangChain prompt template
lc_prompt = PromptTemplate.from_template(prompt_template)

def generate_and_execute_query(user_query: str):
    """
    Generates and executes a DataFrame query based on user input.
    """
    df = pd.read_csv("C:/Users/arthu/OneDrive/Desktop/Repo/LLMProject/ls.csv")
    dict_input = {'df_head':df.head(2).to_string(),'columns':", ".join(df.columns),'user_query':user_query}
    # Create a LangChain LLMChain
    chain = LLMChain(prompt=lc_prompt, llm=llm)

    # Get the code generation from the LLM
    response = chain.invoke(dict_input)
    generated_code = response['text'].strip()
    
    # Print the generated code
    #generated_code = generated_code.pop(0) if generated_code[0] == ' ' or generated_code[0] == '\n' else generated_code
    print("\nGenerated Code:\n", generated_code)
    
    # Prepare the local environment for code execution
    
    local_vars = {"df": df, "clear_string": clear_string}
    
    # Execute the generated code
    try:
        exec(generated_code, globals(), local_vars)
        result = local_vars.get('result', 'No result found')
    except Exception as e:
        result = f"Error executing generated code: {e}"
        user_query = f"Error in previus generated code:{generated_code} Error:{e}, Generate a new code for the query: {user_query}"
        generate_and_execute_query(user_query)
    print(result)
    return result

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    result = generate_and_execute_query(user_input)
    print("\nQuery Result:\n", result)