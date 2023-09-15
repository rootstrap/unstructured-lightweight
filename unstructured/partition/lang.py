from typing import List

import iso639
<<<<<<< HEAD
from langdetect import DetectorFactory, detect_langs
=======
>>>>>>> eb8ce891 (chore: function to map between standard and Tesseract language codes (#1421))

from unstructured.logger import logger

# pytesseract.get_languages(config="") only shows user installed language packs,
# so manually include the list of all currently supported Tesseract languages
PYTESSERACT_LANGS = [
    "afr",
    "amh",
    "ara",
    "asm",
    "aze",
    "aze_cyrl",
    "bel",
    "ben",
    "bod",
    "bos",
    "bre",
    "bul",
    "cat",
    "ceb",
    "ces",
    "chi_sim",
    "chi_sim_vert",
    "chi_tra",
    "chi_tra_vert",
    "chr",
    "cos",
    "cym",
    "dan",
    "deu",
    "div",
    "dzo",
    "ell",
    "eng",
    "enm",
    "epo",
    "equ",
    "est",
    "eus",
    "fao",
    "fas",
    "fil",
    "fin",
    "fra",
    "frk",
    "frm",
    "fry",
    "gla",
    "gle",
    "glg",
    "grc",
    "guj",
    "hat",
    "heb",
    "hin",
    "hrv",
    "hun",
    "hye",
    "iku",
    "ind",
    "isl",
    "ita",
    "ita_old",
    "jav",
    "jpn",
    "jpn_vert",
    "kan",
    "kat",
    "kat_old",
    "kaz",
    "khm",
    "kir",
    "kmr",
    "kor",
    "kor_vert",
    "lao",
    "lat",
    "lav",
    "lit",
    "ltz",
    "mal",
    "mar",
    "mkd",
    "mlt",
    "mon",
    "mri",
    "msa",
    "mya",
    "nep",
    "nld",
    "nor",
    "oci",
    "ori",
    "osd",
    "pan",
    "pol",
    "por",
    "pus",
    "que",
    "ron",
    "rus",
    "san",
    "sin",
    "slk",
    "slv",
    "snd",
    "snum",
    "spa",
    "spa_old",
    "sqi",
    "srp",
    "srp_latn",
    "sun",
    "swa",
    "swe",
    "syr",
    "tam",
    "tat",
    "tel",
    "tgk",
    "tha",
    "tir",
    "ton",
    "tur",
    "uig",
    "ukr",
    "urd",
    "uzb",
    "uzb_cyrl",
    "vie",
    "yid",
    "yor",
]

<<<<<<< HEAD

DetectorFactory.seed = 0  # do this inside a function?

=======
>>>>>>> eb8ce891 (chore: function to map between standard and Tesseract language codes (#1421))

def prepare_languages_for_tesseract(languages: List[str] = ["eng"]):
    """
    Entry point: convert languages (list of strings) into tesseract ocr langcode format (uses +)
    """
    converted_languages = list(
        filter(None, [convert_language_to_tesseract(lang) for lang in languages]),
    )
    return "+".join(converted_languages)


def convert_old_ocr_languages_to_languages(ocr_languages: str):
    """
    Convert ocr_languages parameter to list of langcode strings.
    Assumption: ocr_languages is in tesseract plus sign format
    """

    return ocr_languages.split("+")


def convert_language_to_tesseract(lang: str) -> str:
    """
    Convert a language code to its tesseract formatted and recognized langcode(s), if supported.
    """
    # if language is already tesseract langcode, return it immediately
    # this will catch the tesseract special cases equ and osd
    # NOTE(shreya): this may catch some cases of choosing between tesseract code variants for a lang
    if lang in PYTESSERACT_LANGS:
        return lang

    # get iso639 language object
    try:
        lang_iso639 = iso639.Language.match(lang.lower())
    except iso639.LanguageNotFoundError:
        logger.warning(f"{lang} is not a valid standard language code.")
        return ""

    # tesseract uses 3 digit codes (639-3, 639-2b, etc) as prefixes, with suffixes for orthography
    # use first 3 letters of tesseract codes for matching to standard codes
    pytesseract_langs_3 = {lang[:3] for lang in PYTESSERACT_LANGS}

    # try to match ISO 639-3 code
    if lang_iso639.part3 in pytesseract_langs_3:
        matched_langcodes = _get_all_tesseract_langcodes_with_prefix(lang_iso639.part3)
        return "+".join(matched_langcodes)

    # try to match ISO 639-2b
    elif lang_iso639.part2b in pytesseract_langs_3:
        matched_langcodes = _get_all_tesseract_langcodes_with_prefix(lang_iso639.part2b)
        return "+".join(matched_langcodes)

    # try to match ISO 639-2t
    elif lang_iso639.part2t in pytesseract_langs_3:
        matched_langcodes = _get_all_tesseract_langcodes_with_prefix(lang_iso639.part2t)
        return "+".join(matched_langcodes)

    else:
        logger.warning(f"{lang} is not a language supported by Tesseract.")
        return ""


def _get_all_tesseract_langcodes_with_prefix(prefix: str):
    """
    Get all matching tesseract langcodes with this prefix (may be one or multiple variants).
    """
    return [langcode for langcode in PYTESSERACT_LANGS if langcode.startswith(prefix)]


def _convert_to_standard_langcode(lang: str) -> str:
    """
    Convert a language code to the standard internal language code format.
    """
    # convert to standard ISO 639-3 language code
    lang_iso639 = iso639.Language.match(lang[:3].lower())
    return lang_iso639.part3


def detect_languages(
    text: str,
    languages: List[str] = ["auto"],
) -> List[str]:
    if text.strip() == "":
        return ["eng"]  # english as default

    if languages and "auto" not in languages:
        doc_languages = [_convert_to_standard_langcode(lang) for lang in languages]
    else:
        langdetect_result = detect_langs(text)  # list of Language objects

        # NOTE(robinson) - Chinese gets detected with codes zh-cn, zh-tw, zh-hk for various
        # Chinese variants. We normalizes these because there is a single model for Chinese
        # machine translation

        langdetect_langs = [
            _convert_to_standard_langcode("zh")
            if langobj.lang.startswith("zh")
            else _convert_to_standard_langcode(langobj.lang)
            for langobj in langdetect_result
        ]

        # remove duplicate chinese (if exists) without modifying order
        doc_languages = []
        for lang in langdetect_langs:
            if lang not in doc_languages:
                doc_languages.append(lang)

    return doc_languages