def formatKeyValue(key, value, isEnv=False):
    _value = f"${{{value}}}" if isEnv else value
    return f"{key}={_value}"


def splitKV(str):
    return str.split("=")


def splitEnv(str):
    return None if str.startswith('#') or not str.strip() else splitKV(str)
