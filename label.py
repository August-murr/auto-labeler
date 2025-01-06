import os
import json
from github import Github
from openai import OpenAI

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
prompt = f"""You are a Github Issues Auto-labeller bot on Hugging Faces TRL(transformers reinforcement learning) library.
            issues labels are: {",".join(fulldescription_labels)}.
            Guess from the following issue title and description what are the appropriate labels name (comma separated).
            The decision must be driven by your knowledge of Hugging Face TRL and label description if there is no description use label name
            specially pay attention to the specific methods,trainers or packages mentioned in the issue to label them.
            Reply the label name extacly the way it's shown to you for example: ❓ question, 🏋 Online DPO, ✨ enhancement
            It is possible that no valid labels are applicable in that case respond empty string.
            Title: {issue['title']}
            Description: {issue['body']}
        """

client = OpenAI()

print(prompt)
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
)

print(response)

labels = response.choices[0].message.content.strip().split(',') 

print("Now labelling")
for label in labels:
    label = label.strip()
    if label: 
        print(f"adding label {label}")
        issue_app.add_to_labels(label)
print("Labelling done ...")
