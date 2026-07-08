class WordGroupingError(ValueError):
    """Raised when a MusicXML syllabic (begin/middle/end) sequence is malformed."""


class SyllableCountMismatchError(ValueError):
    """Raised when the number of syllables a word spans in the score doesn't
    match the number of vowel nuclei found in its G2P phoneme sequence."""

    def __init__(self, word, expected, phonemes, nucleus_count, note_indices, source="g2p"):
        self.word = word
        self.expected = expected
        self.phonemes = phonemes
        self.nucleus_count = nucleus_count
        self.note_indices = note_indices
        self.source = source
        super().__init__(
            "Syllable count mismatch for word '{word}' (source={source}): "
            "score expects {expected} syllable(s) (notes {note_indices}), "
            "but phonemes {phonemes} contain {nucleus_count} vowel nucleus/nuclei. "
            "Fix the score's syllabic tags or supply an override entry for this word.".format(
                word=word,
                source=source,
                expected=expected,
                note_indices=note_indices,
                phonemes=phonemes,
                nucleus_count=nucleus_count,
            )
        )


class DictionaryConflictError(ValueError):
    """Raised when the same literal lyric fragment text requires different
    phonemes in different words within the same song (PhonemeTable lookup has
    no per-note context and cannot disambiguate this)."""

    def __init__(self, fragment, phonemes_a, phonemes_b, word_a, word_b):
        self.fragment = fragment
        self.phonemes_a = phonemes_a
        self.phonemes_b = phonemes_b
        self.word_a = word_a
        self.word_b = word_b
        super().__init__(
            "Fragment '{fragment}' requires different phonemes in different words: "
            "{phonemes_a} (from '{word_a}') vs {phonemes_b} (from '{word_b}'). "
            "Supply an override entry that applies uniformly to this spelling.".format(
                fragment=fragment,
                phonemes_a=phonemes_a,
                word_a=word_a,
                phonemes_b=phonemes_b,
                word_b=word_b,
            )
        )
