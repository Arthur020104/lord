from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
class Manager(BaseModel):
    answer: str = Field(description="Explain why you chose that node based on the chat history")
    node: str = Field(description="Name of the node to be called next")

manager_parser = JsonOutputParser(pydantic_object=Manager)

manager_output_parser_str = f'{{{{"The output format must follow the instructions: {manager_parser.get_format_instructions().replace("{", "{{").replace("}", "}}")}"}}}}'