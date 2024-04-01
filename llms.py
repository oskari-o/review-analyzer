from openai import OpenAI
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import tiktoken

def get_gpt4_completion(prompt, system_prompt, api_key):
    """Returns the completion from GPT-4."""
    tokens = count_gpt4_tokens(prompt)
    print(f"\n\nNew Prompt with {tokens} - Response:\n\n")
    client = OpenAI(api_key=api_key)
    stream = client.chat.completions.create(
      model="gpt-4-turbo-preview",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
      ],
      stream=True
    )
    response = ""
    for chunk in stream:
      if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
        response += chunk.choices[0].delta.content
    return response

def count_gpt4_tokens(prompt: str):
    """Returns the number of tokens in the prompt."""
    encoding = tiktoken.encoding_for_model('gpt-4-turbo-preview')
    token_count = len(encoding.encode(prompt))
    return token_count

def get_mistral_completion(prompt, system_prompt, api_key):
    """Returns the completion from Mistral 7B."""
    client = MistralClient(api_key=api_key)
    stream = client.chat_stream(
      model="open-mistral-7b",
      messages=[
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=prompt),
      ]
    )
    response = ""
    for chunk in stream:
      if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
        response += chunk.choices[0].delta.content
    return response
    
    