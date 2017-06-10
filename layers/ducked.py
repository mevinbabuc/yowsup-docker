from .duckduckgo import get_zci


def get_results(message):

    if message.lower().startswith("what is"):
        return get_zci(message.lstrip('what is'))
