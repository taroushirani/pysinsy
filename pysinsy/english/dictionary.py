import os
import tempfile
from contextlib import contextmanager

from .errors import DictionaryConflictError, SyllableCountMismatchError
from .g2p import word_to_phonemes
from .syllabify import split_into_syllables

_CONF_CONTENT = (
    'LANGUAGE_INFO="ENG"\n'
    'VOWELS="AA0,AA1,AA2,AE0,AE1,AE2,AH0,AH1,AH2,AO0,AO1,AO2,AW0,AW1,AW2,'
    "AY0,AY1,AY2,EH0,EH1,EH2,ER0,ER1,ER2,EY0,EY1,EY2,IH0,IH1,IH2,IY0,IY1,IY2,"
    'OW0,OW1,OW2,OY0,OY1,OY2,UH0,UH1,UH2,UW0,UW1,UW2"\n'
)


def _resolve_word_syllables(word, k, note_indices, overrides):
    key = word.lower()
    if key in overrides:
        syllables = overrides[key]
        if len(syllables) != k:
            raise SyllableCountMismatchError(
                word=word,
                expected=k,
                phonemes=[p for syl in syllables for p in syl],
                nucleus_count=len(syllables),
                note_indices=note_indices,
                source="override",
            )
        return syllables

    phonemes = word_to_phonemes(word)
    return split_into_syllables(phonemes, k, word, note_indices)


def compute_fragment_table(words, overrides):
    """Resolve each word's syllable phonemes and build a fragment-text ->
    phoneme-list mapping (one entry per distinct note-level lyric fragment).

    Raises:
        DictionaryConflictError: if the same literal fragment text is
            required to map to two different phoneme lists (PhonemeTable
            lookups have no per-note context to disambiguate this).
    """
    table = {}
    origin = {}

    for word in words:
        k = len(word.fragments)
        note_indices = [f.note_index for f in word.fragments]
        syllables = _resolve_word_syllables(word.text, k, note_indices, overrides)

        for fragment, syllable_phonemes in zip(word.fragments, syllables):
            key = fragment.lyric
            if key in table and table[key] != syllable_phonemes:
                raise DictionaryConflictError(
                    fragment=key,
                    phonemes_a=table[key],
                    phonemes_b=syllable_phonemes,
                    word_a=origin[key],
                    word_b=word.text,
                )
            table[key] = syllable_phonemes
            origin[key] = word.text

    return table


@contextmanager
def build_temp_dic_dir(fragment_table):
    """Write a sinsy PhonemeTable-format dictionary (+ conf + empty macron
    file) for `fragment_table` into a temporary directory, yielding its path.
    """
    for fragment in fragment_table:
        if not fragment or fragment.split() != [fragment]:
            raise ValueError(
                "Lyric fragment {0!r} contains whitespace or is empty; it "
                "cannot be used as a sinsy PhonemeTable key.".format(fragment)
            )

    with tempfile.TemporaryDirectory(prefix="pysinsy_english_") as tmp_dir:
        table_path = os.path.join(tmp_dir, "english.utf_8.table")
        conf_path = os.path.join(tmp_dir, "english.utf_8.conf")
        macron_path = os.path.join(tmp_dir, "english.macron")

        with open(table_path, "w", encoding="utf-8") as f:
            for fragment, phonemes in fragment_table.items():
                f.write("{0} {1}\n".format(fragment, " ".join(phonemes)))

        with open(conf_path, "w", encoding="utf-8") as f:
            f.write(_CONF_CONTENT)

        open(macron_path, "w", encoding="utf-8").close()

        yield tmp_dir
