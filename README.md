# Auto Labeller Bot

## Overview

The Auto Labeller Bot is a GitHub Action that automatically labels issues using a Hugging Face model. When an issue is opened, the bot uses the Hugging Face API to predict the appropriate labels based on the issue's content.

## Features

- Automatically labels GitHub issues using a specified Hugging Face model.
- Supports custom models by specifying the model name.
- Uses the Hugging Face Inference Endpoint for predictions.

## Requirements

- A Hugging Face API token.
- A GitHub repository with issues enabled.

## Setup

1. **Add Secrets**: Add your Hugging Face API token to your repository secrets. Go to your repository settings, then to the "Secrets and variables" section, and add a new secret named `HF_API_KEY`.

2. **Copy Workflow File**: Copy the `usage.yml` file into the `.github/workflows` directory of your repository.

    ```yaml
    name: "Hugging Face Issue Labeler"
    on:
      issues:
        types: opened

    jobs:
      triage:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - uses: August-murr/auto-labeler@main
            with:
                hf-api-key: ${{ secrets.HF_API_KEY }}
    ```

3. **Configure Model Name**: In the `usage.yml` file, you can specify the model name you want to use. The default model is `meta-llama/Llama-3.3-70B-Instruct`.

## Usage

Once the setup is complete, the bot will automatically label new issues based on the specified Hugging Face model. The bot will analyze the issue's title and body to predict the most appropriate labels.

## Example

When an issue is opened, the bot will:

1. Retrieve the issue content.
2. Generate a prompt for the Hugging Face model.
3. Use the Hugging Face API to get label predictions.
4. Apply the predicted labels to the issue.

## Contributing

If you want to contribute to this project, feel free to open a pull request or submit an issue.
