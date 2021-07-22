# Introduction
The goal of this project is to provide a sample to create Azure DevOps policies, more specifically: Build Validation, Minimum number of reviewers and Required reviewers policies, throught the Azure DevOps SDK.

You can also use the [build pipeline](azure-pipelines.yml) to automate policy creation and updating.

## Requirements
* Python 3.8+ (Local-only config)
* Git 2.25.1+ (Local-only config)

## Running
1. Create a [Personal Access Token](https://docs.microsoft.com/pt-br/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page)

2. Replace *%PERSONAL_ACCESS_TOKEN%* with token created in the step one:
```sh
PAT='%PERSONAL_ACCESS_TOKEN%' python app.py
```