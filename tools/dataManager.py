import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.tools import PythonAstREPLTool
from langchain.tools import Tool
from unidecode import unidecode
from secret.apiOpenAI import api_key
import sys
sys.path.append('../')

llm = ChatOpenAI(api_key=api_key, temperature=0, model="gpt-3.5-turbo")

def clear_string(input_string):
    cleaned_string = unidecode(input_string)
    return cleaned_string.lower()

df = pd.read_csv("C:/Users/arthu/OneDrive/Desktop/Repo/llm/ls.csv")

shortest_row_length = min(len(str(row)) for row in df.itertuples(index=False))
print(shortest_row_length)

data_frame_reader = PythonAstREPLTool(
    locals={"df": df, "clear_string": clear_string},
    name="DataFrame_Reader",
    description=f"A tool to read columns from a DataFrame using Python code. 'df' is already loaded in the locals, you need to execute Python code to read from the DataFrame. 'df' has the following columns: {df.columns}. Always remove diacritics in comparisons both from the base and the search (before searching, remove diacritics from the database), standardize the search without using case.",
)

tools = [data_frame_reader]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"You are a data search assistant. You will receive questions/codes and return answers based on your 'data reading' function that uses Python code. Focus on answering questions with just the data, if necessary add information, do not show more than 2 properties unless requested. Always show the property index as id, along with all the property columns, id and location fields should come first. And if a field named id is received, search the base as index using iloc, loc. Start with a specific search and if nothing is found, expand the search. For example, if the search is for shopping park and landscape street and nothing is found, perform the search for shopping park. Do not use information like near x as a search query. df.head(2) = {df.head(2)} perform the search df[df['Neighborhood'].apply(clear_string).str.contains(clear_string('shopping park'))] to find properties in the shopping park neighborhood. Return only valid information (all the 'in' values), such as property values, never return just the search keys. example of a complete search df[(df['City'].apply(clear_string) == clear_string('uberlândia')) & (df['UnitType'].apply(clear_string) == clear_string('house')) & (df['Bedrooms'] == 4) & (df['Bathrooms'] == 5) & (df['Suites'] == 4) & (df['Neighborhood'].apply(clear_string).str.contains(clear_string('shopping park'))) & (df['ParkingSpaces'] == 4) & (df['Price'] >= 2025000) & (df['Price'] <= 2475000)][:5] Never alter the information retrieved from the database. Do not summarize or hide information.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
executor_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
)

def execute(input:str):
    response = agent_chain.invoke({"input":input})
    return response['output']

read = Tool.from_function(
    func= execute,
     name="DataFrame_Reader",
    description=f"An assistant for database search, pass the questions to it and it will return the answer. Just tell it what you are looking for and it will respond. Must be specific.",
)

if __name__ == "__main__":
    print(execute(input("Enter your question:")))
