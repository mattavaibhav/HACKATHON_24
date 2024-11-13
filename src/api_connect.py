# Import prerequisite libraries
import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv('AZURE_OAI_KEY')
OPENAI_API_ENDPOINT = os.getenv('AZURE_OAI_ENDPOINT')
DEPLOYMENT_NAME = os.getenv('AZURE_OAI_DEPLOYMENT')
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")

# open AI connection
client = AzureOpenAI(
    azure_endpoint=OPENAI_API_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version="2024-08-01-preview"
)

pattern_doc = r"\[doc\d+\]"

# Configure your data source
extension_config = {"data_sources": [
    {
        "type": "azure_search",
        "parameters": {
            "endpoint": AZURE_SEARCH_ENDPOINT,
            "index_name": AZURE_SEARCH_INDEX,
            "authentication": {
                "type": "api_key",
                "key": AZURE_SEARCH_KEY,
            }
        }
    }
],
}


def get_response(messages: list, stream: bool = False):
    # Send a completion call to generate an answer
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,  # model = "deployment_name".
        messages=messages,
        stream=stream,
        extra_body=extension_config
    )
    return parse_response(response)


def parse_response(stream):
    citations = set()
    contents = []
    for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        content = re.sub(pattern_doc,'', content)
        contents.append(content)
        if 'context' in chunk.choices[0].delta.model_extra:
            message_citations = chunk.choices[0].delta.model_extra['context']['citations']
            for citation in message_citations:
                title = citation['title']
                if title:
                    citations.add(title)
    if citations:
        contents.append(f"\n\n**References looked up**: {', '.join(citations)}")
    return iter(contents)
