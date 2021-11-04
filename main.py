import oyaml as yaml
from PyInquirer import prompt
from shutil import copyfile

from utils import formatKeyValue, splitKV, splitEnv

from questions import hostLikeQuestion, answer_key, choice_dot_env, choice_service_name, choice_existing, serviceListQuestion

try:
    with open(".env", "r") as env_file:
        try:
            env_vars = {x[0]: x[1]
                        for x in filter(None, map(splitEnv, env_file))}
        finally:
            env_file.close()
except FileNotFoundError:
    with open(".env.example", "r") as example_env_file:
        try:
            env_vars = {x[0]: x[1] for x in filter(
                None, map(splitEnv, example_env_file))}
        finally:
            example_env_file.close()


def addServiceLink(service, other_service_name):
    if other_service_name not in service.get("links", []):
        service.setdefault("links", []).append(
            other_service_name)
    if other_service_name not in service.get("depends_on", []):
        service.setdefault("depends_on", []).append(
            other_service_name)


def mapEnvVar(key_value, service, service_list_question):
    key, value = key_value
    if "host" in key.lower():
        answers = prompt(hostLikeQuestion(key))
        if answers[answer_key] == choice_dot_env:
            print(f"Using .env key name for host-like key")
            line = formatKeyValue(key, key, True)
        elif answers[answer_key] == choice_service_name:
            print(f"Using service name for host-like key")
            service_answers = prompt(service_list_question)
            other_service_name = service_answers[answer_key]
            addServiceLink(service, other_service_name)
            line = formatKeyValue(key, other_service_name)
        elif answers[answer_key] == choice_existing:
            print(f"Using existing value for host-like key")
            line = formatKeyValue(key, value)
    elif key in env_vars:
        print(f"Found key in .env {key}, replacing with .env key name")
        line = formatKeyValue(key, key, True)
    else:
        print(
            f"No matching key name found in .env {key}, using existing value")
        line = formatKeyValue(key, value)
    return line


def loadYaml(filename):
    with open(filename, "r") as stream:
        try:
            return yaml.load(stream, Loader=yaml.BaseLoader)
        except yaml.YAMLError as exc:
            print(exc)
        finally:
            stream.close()


try:
    docker_compose_file = loadYaml("docker-compose.yml")
except FileNotFoundError:
    docker_compose_file = loadYaml("docker-compose.example.yml")

environment_key = "environment"
services_key = "services"

service_list = list(docker_compose_file[services_key].keys())
for service_name in docker_compose_file[services_key]:
    service = docker_compose_file[services_key][service_name]
    if environment_key not in service:
        continue
    service_environment = service[environment_key]
    print(f"Iterating over service {service_name}'s environment variables")

    other_services_list = service_list.copy()
    other_services_list.remove(service_name)

    service_list_question = serviceListQuestion(other_services_list)

    service_environment_list = map(splitKV, service_environment) if type(service_environment) is list else map(
        lambda key: [key, service_environment[key]], service_environment)

    docker_compose_file[services_key][service_name][environment_key] = list(map(lambda key_value: mapEnvVar(
        key_value, service, service_list_question), service_environment_list))

with open("docker-compose-updated.yml", "w") as docker_compose_stream:
    try:
        yaml.dump(docker_compose_file, docker_compose_stream)
    except yaml.YAMLError as exc:
        print(exc)
    finally:
        docker_compose_stream.close()
