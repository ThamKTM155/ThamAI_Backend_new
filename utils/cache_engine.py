# =======================================
# cache_engine.py
# BUILD-39D
# =======================================

CACHE = {}


def get_cache(question):

    return CACHE.get(question)


def save_cache(question, answer):

    CACHE[question] = answer