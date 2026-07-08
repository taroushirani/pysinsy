import re

from .errors import SyllableCountMismatchError

_NUCLEUS_RE = re.compile(r"[012]$")

# Legal English word-initial (onset) consonant clusters, by length.
_LEGAL_ONSETS = {
    3: {"SPR", "STR", "SKR", "SPL", "SKW"},
    2: {
        "PR", "TR", "KR", "BR", "DR", "GR", "FR",
        "PL", "KL", "BL", "GL", "FL", "SL",
        "SP", "ST", "SK", "SM", "SN", "SW",
        "TW", "KW", "DW", "GW",
        "TH", "SH", "CH", "PH", "WH",
        "DH", "ZH", "NG",
    },
}


def _is_vowel(phoneme):
    return bool(_NUCLEUS_RE.search(phoneme))


def _onset_length(consonants):
    """Length of the longest legal onset cluster formed by the *end* of
    `consonants` (the part closest to the following vowel nucleus)."""
    n = len(consonants)
    for length in (3, 2):
        if n >= length and "".join(consonants[n - length:]) in _LEGAL_ONSETS[length]:
            return length
    return 1 if n >= 1 else 0


def split_into_syllables(phonemes, k, word, note_indices=None):
    """Split a flat ARPABET phoneme sequence into exactly `k` syllables using
    vowel-nucleus detection (stress-digit suffix) and maximal-onset
    consonant-cluster splitting.

    Raises:
        SyllableCountMismatchError: if the number of vowel nuclei in
            `phonemes` doesn't equal `k`.
    """
    nucleus_positions = [i for i, p in enumerate(phonemes) if _is_vowel(p)]
    if len(nucleus_positions) != k:
        raise SyllableCountMismatchError(
            word=word,
            expected=k,
            phonemes=phonemes,
            nucleus_count=len(nucleus_positions),
            note_indices=note_indices,
        )

    if k <= 1:
        return [list(phonemes)]

    syllables = [[] for _ in range(k)]
    syllables[0].extend(phonemes[: nucleus_positions[0] + 1])

    for idx in range(1, k):
        prev_nucleus = nucleus_positions[idx - 1]
        cur_nucleus = nucleus_positions[idx]
        cluster = phonemes[prev_nucleus + 1 : cur_nucleus]
        onset_len = _onset_length(cluster)
        coda_len = len(cluster) - onset_len
        syllables[idx - 1].extend(cluster[:coda_len])
        syllables[idx].extend(cluster[coda_len:])
        syllables[idx].append(phonemes[cur_nucleus])

    syllables[-1].extend(phonemes[nucleus_positions[-1] + 1 :])

    return syllables
