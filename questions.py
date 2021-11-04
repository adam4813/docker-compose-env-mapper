answer_key = "answer"


choice_dot_env = '.env'
choice_service_name = 'service name'
choice_existing = 'existing value'


def hostLikeQuestion(key_name):
    return [
        {
            "type": "list",
            "name": answer_key,
            "message": f"Key {key_name} contains \"host\", determining which to use: ",
            "choices": [choice_dot_env,
                        choice_service_name,
                        choice_existing],
        }
    ]


def serviceListQuestion(service_list):
    return [
        {
            "type": "list",
            "name": answer_key,
            "message": "Please pick a serivce name",
            "choices": service_list,
        }
    ]
