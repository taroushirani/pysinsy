import os
import re
import tempfile

import pytest

pytest.importorskip("g2p_en")

import pysinsy
from pysinsy.english.dictionary import compute_fragment_table
from pysinsy.english.errors import (
    DictionaryConflictError,
    SyllableCountMismatchError,
    WordGroupingError,
)
from pysinsy.english.overrides import load_overrides
from pysinsy.english.wordgrouping import (
    SYLLABIC_BEGIN,
    SYLLABIC_END,
    SYLLABIC_MIDDLE,
    SYLLABIC_SINGLE,
    NoteFragment,
    Word,
    group_notes_into_words,
)

FIXTURE = os.path.join(os.path.dirname(__file__), "song_english_lyrics.xml")

# HTS full-context labels reserve these as delimiters between fields.
_HTS_DELIMITERS = set("@^-+=_%~![$]|&#;")


def test_extract_fullcontext_english_uses_eng_tag_and_safe_phonemes():
    labels = pysinsy.extract_fullcontext_english(FIXTURE)
    assert len(labels) > 0

    joined = "\n".join(labels)
    assert "@ENG" in joined  # language tag propagated instead of JPN
    assert "@JPN" not in joined

    for label in labels:
        current_phoneme = label.split("-", 1)[1].split("+", 1)[0]
        if current_phoneme in ("xx", "pau", "sil"):
            continue
        assert re.match(r"^[A-Z0-9]+$", current_phoneme), current_phoneme
        assert not (_HTS_DELIMITERS & set(current_phoneme))


def test_overrides_path_takes_priority_over_g2p():
    with tempfile.TemporaryDirectory() as d:
        overrides_path = os.path.join(d, "overrides.tsv")
        with open(overrides_path, "w") as f:
            f.write("song\tS AH1 NG\n")  # deliberately different from g2p_en's own output

        labels = pysinsy.extract_fullcontext_english(FIXTURE, overrides_path=overrides_path)
        joined = "\n".join(labels)
        assert "AH1" in joined


def test_word_grouping_error_on_orphan_middle():
    notes = [{"lyric": "ti", "syllabic": SYLLABIC_MIDDLE, "is_rest": False, "duration": 4}]
    with pytest.raises(WordGroupingError):
        group_notes_into_words(notes)


def test_word_grouping_error_on_unterminated_word():
    notes = [{"lyric": "beau", "syllabic": SYLLABIC_BEGIN, "is_rest": False, "duration": 4}]
    with pytest.raises(WordGroupingError):
        group_notes_into_words(notes)


def test_word_grouping_skips_rests_and_empty_lyrics():
    notes = [
        {"lyric": "beau", "syllabic": SYLLABIC_BEGIN, "is_rest": False, "duration": 4},
        {"lyric": "", "syllabic": SYLLABIC_SINGLE, "is_rest": True, "duration": 4},
        {"lyric": "ful", "syllabic": SYLLABIC_END, "is_rest": False, "duration": 4},
    ]
    words = group_notes_into_words(notes)
    assert len(words) == 1
    assert words[0].text == "beauful"


def test_syllable_count_mismatch_error():
    # "wonderful" has 3 vowel nuclei per g2p_en, but only 2 notes are supplied.
    word = Word(
        text="wonderful",
        fragments=[
            NoteFragment(0, "won", SYLLABIC_BEGIN),
            NoteFragment(1, "derful", SYLLABIC_END),
        ],
    )
    with pytest.raises(SyllableCountMismatchError) as excinfo:
        compute_fragment_table([word], overrides={})
    assert excinfo.value.expected == 2
    assert excinfo.value.nucleus_count == 3


def test_dictionary_conflict_error_on_ambiguous_fragment():
    # The fragment "foo" is required to mean two different things depending on
    # whether it's the whole word "foo" or the first syllable of "foobar".
    word_a = Word(text="foo", fragments=[NoteFragment(0, "foo", SYLLABIC_SINGLE)])
    word_b = Word(
        text="foobar",
        fragments=[
            NoteFragment(1, "foo", SYLLABIC_BEGIN),
            NoteFragment(2, "bar", SYLLABIC_END),
        ],
    )
    overrides = {
        "foo": [["F", "UW1"]],
        "foobar": [["F", "UW1", "B"], ["AA1", "R"]],
    }
    with pytest.raises(DictionaryConflictError):
        compute_fragment_table([word_a, word_b], overrides=overrides)


def test_overrides_are_used_instead_of_g2p():
    with tempfile.TemporaryDirectory() as d:
        overrides_path = os.path.join(d, "overrides.tsv")
        with open(overrides_path, "w") as f:
            f.write("gizmo\tG IH1 Z . M OW1\n")

        overrides = load_overrides(overrides_path)
        word = Word(
            text="gizmo",
            fragments=[
                NoteFragment(0, "giz", SYLLABIC_BEGIN),
                NoteFragment(1, "mo", SYLLABIC_END),
            ],
        )
        table = compute_fragment_table([word], overrides)
        assert table["giz"] == ["G", "IH1", "Z"]
        assert table["mo"] == ["M", "OW1"]
