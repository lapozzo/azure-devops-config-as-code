from azure.devops.connection import Connection
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import config
import json
import logging
import os

logging.basicConfig(level=logging.INFO)

# Security Groups for repo policies
GROUP_NAME = 'Developers'

ORGANIZATON_URL = 'https://dev.azure.com/organizationname'

# projects names and repositories to apply the policies
PROJECTS = [{
    'name': 'Project1',
    'repos': ['project1']
}]

# Get Azure DevOps Access Token - Personal Access Token
if 'PAT' not in os.environ:
    raise Exception(
        'Personal Access Token it is required')
else:
    PERSONAL_ACCESS_TOKEN = os.environ['PAT']

# get clients for Azure DevOps APIs
credentials = BasicAuthentication(
    '', PERSONAL_ACCESS_TOKEN)
connection = Connection(base_url=ORGANIZATON_URL, creds=credentials)
policy_client = connection.clients.get_policy_client()
git_client = connection.clients.get_git_client()
identity_client = connection.clients.get_identity_client()
graph_client = connection.clients_v6_0.get_graph_client()


def get_security_group(name, project):
    get_groups_response = graph_client.list_groups()
    index = 0
    while get_groups_response is not None:
        for group in get_groups_response.graph_groups:
            if(group.principal_name == "[{}]\{}".format(project, name)):
                return group
            index += 1
        if get_groups_response.continuation_token is not None and get_groups_response.continuation_token != "":
            # Get the next page of groups
            get_groups_response = graph_client.list_groups(
                continuation_token=get_groups_response.continuation_token)
        else:
            # All groups have been retrieved
            get_groups_response = None
    raise Exception(
        "Security Group {} not found for project {}".format(name, project))


def load_policy_template(template_name):
    with open('templates/'+template_name, 'r') as json_file:
        return json.load(json_file)


def get_existent_policy(policy, project):
    display_name = policy['type']['displayName']
    type_id = policy['type']['id']
    policy_confs = policy_client.get_policy_configurations(project=project)
    for policy in policy_confs.value:
        if(policy.type.display_name == display_name and policy.type.id == type_id):
            return policy


def get_repository_by_name(name, project):
    get_repos_response = git_client.get_repositories(project)
    for repo in get_repos_response:
        if repo.name == name:
            return repo
    raise Exception(
        "Repository {} not found for project {}".format(name, project))


def save_policy(policy, project):
    existentPolicy = get_existent_policy(policy, project)
    if existentPolicy:
        logging.info("Updating Policy: {}, Project: {}".format(
            policy['type']['id'], project))
        policy_client.update_policy_configuration(
            configuration=policy, project=project, configuration_id=existentPolicy.id)
    else:
        logging.info("Creating Policy: {}, Project: {}".format(
            policy['type']['id'], project))
        policy_client.create_policy_configuration(
            configuration=policy, project=project)


def apply_required_reviewers_policy(project, repo):
    policy = load_policy_template('required_reviewers.json')
    repo = get_repository_by_name(repo, project)
    for scope in policy['settings']['scope']:
        scope['repositoryId'] = repo.id

    reviewers = list()
    sg = get_security_group(GROUP_NAME, project)
    reviewers.append(sg.origin_id)
    policy['settings']['requiredReviewerIds'] = reviewers

    save_policy(policy, project)


def apply_min_reviewers_policy(project, repo):
    policy = load_policy_template('min_reviewers.json')
    repo = get_repository_by_name(repo, project)
    for scope in policy['settings']['scope']:
        scope['repositoryId'] = repo.id

    save_policy(policy, project)


def apply_build_validation_policy(project, repo):
    policy = load_policy_template('build_validation.json')
    repo = get_repository_by_name(repo, project)
    for scope in policy['settings']['scope']:
        scope['repositoryId'] = repo.id

    save_policy(policy, project)

def main():
    for project in config.projects:
        for repo in project['repos']:
            logging.info(
                "Applying policies for Project {}, Repository {} ".format(project, repo))
            apply_build_validation_policy(project['name'], repo)
            apply_min_reviewers_policy(project['name'], repo)
            apply_required_reviewers_policy(project['name'], repo)


if __name__ == "__main__":
    main()
