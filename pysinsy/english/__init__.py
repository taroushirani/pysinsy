from .dictionary import build_temp_dic_dir, compute_fragment_table
from .errors import DictionaryConflictError, SyllableCountMismatchError, WordGroupingError
from .overrides import load_overrides
from .wordgrouping import group_notes_into_words

__all__ = [
    "extract_fullcontext_english",
    "DictionaryConflictError",
    "SyllableCountMismatchError",
    "WordGroupingError",
]


def extract_fullcontext_english(xml_path, overrides_path=None):
    """Extract HTS full-context labels for a MusicXML file with English
    lyrics (words split across notes via <lyric>/<syllabic>).

    Args:
        xml_path (str): Path to a MusicXML file with English lyrics.
        overrides_path (str, optional): Path to a TSV file of manual
            word -> syllable-phoneme overrides, checked before g2p_en.

    Returns:
        list of str: HTS full-context label lines.

    Raises:
        WordGroupingError: malformed syllabic begin/middle/end sequence.
        SyllableCountMismatchError: a word's G2P syllable count doesn't
            match how many notes it spans in the score.
        DictionaryConflictError: the same lyric fragment text requires
            different phonemes in two different words in this song.
    """
    from ..sinsy import Sinsy  # local import: avoid a cycle with pysinsy/__init__.py

    sinsy = Sinsy()  # a fresh instance; the shared _global_sinsy dictionary differs per song
    sinsy.loadScoreFromMusicXML(xml_path)
    notes = sinsy.getNotes()
    words = group_notes_into_words(notes)
    overrides = load_overrides(overrides_path)
    fragment_table = compute_fragment_table(words, overrides)

    with build_temp_dic_dir(fragment_table) as dic_dir:
        if not sinsy.setLanguages("e", dic_dir):
            raise RuntimeError("Failed to configure English dictionary/config for sinsy")
        labels = sinsy.createLabelData(False, 1, 1).getData()

    sinsy.clearScore()
    return labels
