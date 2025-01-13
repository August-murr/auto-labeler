import os
import json
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
fulldescription_labels = [f"(name:\"{label.name}\",description:\"{label.description}\")" for label in repo.get_labels()]


print(f"""Guessing among : {",".join(available_labels)}""")
issue = event['issue']        
prompt = f"""issues labels are: {",".join(fulldescription_labels)}.
            Guess from the following issue title and description what the appropriate label names are (comma separated).
            The decision must be driven by your knowledge of Hugging Face TRL and label description if there is no description use label name
            specially pay attention to the specific methods,trainers or packages mentioned in the issue to label them.
            Reply the label name extacly the way it's shown to you for example: ❓ question, 🏋 Online DPO, ✨ enhancement
            It is possible that no valid labels are applicable in that case respond empty string.
            Title: {issue["title"]}
            Description: {issue["body"][:4000]}
        """

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
client = InferenceClient(model=MODEL_NAME, token=HF_API_KEY)


print(prompt)
response = client.chat_completion(messages=[
    {"role": "system", "content": "You are an Github Issues Auto-labeller bot on Hugging Faces TRL(transformers reinforcement learning) library."},
    {"role": "user", "content": prompt}], max_tokens=50)

print(response)

labels = [
    unicodedata.normalize("NFKC", lab).replace('\uFE0F', '').strip()
    for lab in response.choices[0].message.content.strip().split(',')
]
labels = [label for label in labels if label in available_labels]

print("Now labelling")
for label in labels:
    label = label.strip()
    if label: 
        print(f"adding label {label}")
        issue_app.add_to_labels(label)
print("Labelling done ...")
