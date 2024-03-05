import base64
import difflib


def exclude_keys(dictionary, keys):
    key_set = set(dictionary.keys()) - set(keys)
    return {key: dictionary[key] for key in key_set}

def str_simularity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def encode_to_base64(buffer):
    return str(base64.b64encode(buffer))[2:-1]