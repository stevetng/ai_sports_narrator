from openai import OpenAI
from exa_py import Exa
import os
import requests

my_secret = os.environ['openai_key']

client = OpenAI(api_key=my_secret)

exa_api_key = os.environ['exa_key']
exa = Exa(exa_api_key)
# notes for self: i'm creating an instance of a Exa class here
# you need to import the Exa class from the Python SDK first, use the API key as a password and then create the Exa class

query = "Articles and discussions about latest political events"
use_autoprompt = True  # Set to True to let Exa optimize the query

# setting up the query to find the recent news articles, and setting the autoprompt parameter to true to then set into the search

options = {
    "num_results": 5,  # Adjust based on how many results you want
    "start_published_date": "2024-02-11",  # Adjust date range as needed
    "end_published_date": "2024-02-18",
    "use_autoprompt": use_autoprompt
}

# dictionaries are similar to JSON files, essentially allowing you to create key value pairs that can be easily changed

search_response = exa.search(query, **options)
# print(search_response)
# creating a variable to store the result returned by the search method from the Exa class instance, the ** is used in the function call to unpack the dictionary into arguments for the function, cool way to parse it

document_ids = [result.id for result in search_response.results]
# creating a list of IDs for the documents I want to smmarize, here we're using list comprehension, where you can parse through a list and return a list
contents_response = exa.get_contents(document_ids)
# print(contents_response.results[0].text)

for result in contents_response.results:
  completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{
          "role":
          "system",
          "content":
          "You are a sports commentator, skilled in describing anything with flair and excitement. Your job is to summarize news article content as if it's a thrilling sports match commentary. As a sports commentator, you're good at describing events with all the cool underlying storylines. You like to include specific details that people at home would like to mention in conversation."
      }, {
          "role": "user",
          "content": result.text
      }])
  print("\n ARTICLE:")
  print(result.url)
  print(completion.choices[0].message.content)
# creating 5 different sports narrations and printing them to console


completion = client.chat.completions.create(
model="gpt-3.5-turbo",
messages=[{
    "role":
    "system",
    "content":
    "You are a sports commentator, skilled in describing anything with flair and excitement. Your job is to summarize news article content as if it's a thrilling sports match commentary. As a sports commentator, you're good at describing events with all the cool underlying storylines. You like to include specific details that people at home would like to mention in conversation."
}, {
    "role": "user",
    "content": contents_response.results[2].text
}])

# creating one sport narration that I'll use to transform into ElevenLabs

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/TVP16pgggr5DzrVe1BTj"

xi_api_key = os.environ['xi_api_key']

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": xi_api_key
}

data = {
  "text": completion.choices[0].message.content,
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

response = requests.post(url, json=data, headers=headers)
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)

# creating a new output.mp3 file and saving the audio from the ElevenLabs API