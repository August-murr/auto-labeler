import os
import json
import re
from textwrap import shorten
from github import Github
from huggingface_hub import InferenceClient
import unicodedata

token = os.getenv('GITHUB_TOKEN')
g = Github(token)

issue_number = os.getenv('GITHUB_EVENT_PATH')
with open(issue_number) as event_file:
    event = json.load(event_file)

repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
issue_app = repo.get_issue(number=event['issue']['number'])
available_labels = [label.name for label in repo.get_labels()]

labels_description = [f'- Label: "{label.name}", description: "{label.description}"' for label in repo.get_labels()]
labels_description = "\n".join(labels_description)

print(f"""Guessing among : {",".join(available_labels)}""")
issue = event['issue']        
body = shorten(issue["body"], width=4000, placeholder="...") 
prompt = f"""Your goal is to predict the appropriate labels for a GitHub issue.
Possible labels are:

{labels_description}

Your prediction must be driven by the knowledge of the library that you may have and label description. 
If there is no label description, rely on the label name. Your prediction should start with a concise reasoning. 
After the reasoning, return your answer as a JSON array containing only the label names. 
If no valid labels are applicable, return an empty JSON array: [].

Example prediction: ["{available_labels[0]}", "{available_labels[1]}"]

Here is the issue:

Title: {issue["title"]}
{body}
"""

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
client = InferenceClient(model=MODEL_NAME, token=HF_API_KEY)


print(prompt)
response = client.chat_completion(messages=[
    {"role": "system", "content": "You are an Github Issues Auto-labeller bot."},
    {"role": "user", "content": prompt}])

print(response)

response = response.choices[0].message.content.strip()

try:
    # Regex to match a JSON array in the output
    match = re.search(r"\[(.*?)\]", response, re.DOTALL)
    if match:
        # Extract the matched JSON string
        json_string = match.group(0)
        # Parse the JSON into a Python list
        labels = json.loads(json_string)
        # Normalize and clean up the labels
        labels = [label.strip() for label in labels]
except (json.JSONDecodeError, AttributeError) as e:
    # Handle parsing errors
    print(f"Error extracting labels: {e}")
    labels = []

labels = [
    unicodedata.normalize("NFKC", lab).replace('\uFE0F', '').strip()
    for lab in labels
]
labels = [label for label in labels if label in available_labels]

print("Now labelling")
for label in labels:
    label = label.strip()
    if label: 
        print(f"adding label {label}")
        issue_app.add_to_labels(label)
print("Labelling done ...")
