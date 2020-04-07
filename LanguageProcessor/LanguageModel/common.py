import json

PUNKT_SUPPORT = ["cs", "da", "nl", "en", "et", "fi", "fr", "de", "el", "it", "no", "po", "pt", "sl", "es", "sv", "tr"]
SNOWBALL_SUPPORT = ["ar", "da", "nl", "en", "fi", "fr", "de", "hu", "it", "no", "pt", "ro", "ru", "es", "sv"]

SUPPORTED_LANGUAGES = {
    "en": "english",
    "de": "german",
    "es": "spanish",
    "fr": "french",
    "zh": "chinese",
    "zh_cn": "chinese cantonese",
    "zh_tw": "chinese taiwanese",
    "ar": "arabic",
    "da": "danish",
    "nl": "dutch",
    "fi": "finnish",
    "hu": "hungarian",
    "it": "italian",
    "no": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sv": "swedish",
    "ja": "japanese",
    "hi": "hindi",
    "cs": "czech",
    "el": "greek",
    "pl": "polish",
    "ms": "bahasa malayu",
    "id": "bahasa indonesia",
    "et": "estonian",
    "sl": "slovene",
    "tr": "turkish",
    "uk": "ukranian",
    "kk": "kazakh",
    "es-MX": "mexican spanish",
    "ko": "korean"
}


def read_file(filename):
    try:
        with open(filename, "r") as file_dp:
            data = json.load(file_dp)
            return data
    except Exception:
        return {}