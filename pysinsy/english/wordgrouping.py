from dataclasses import dataclass
from typing import List, Optional

from .errors import WordGroupingError

SYLLABIC_SINGLE = 0
SYLLABIC_BEGIN = 1
SYLLABIC_MIDDLE = 2
SYLLABIC_END = 3


@dataclass
class NoteFragment:
    note_index: int
    lyric: str
    syllabic: int


@dataclass
class Word:
    text: str
    fragments: List[NoteFragment]


def group_notes_into_words(notes) -> List[Word]:
    """Group notes (as returned by Sinsy.getNotes()) into words, using each
    note's syllabic value (single/begin/middle/end) to find word boundaries.

    Rests and lyric-less notes (e.g. tied continuation notes) are skipped
    without breaking an open word.
    """
    words: List[Word] = []
    current: Optional[List[NoteFragment]] = None

    for note_index, note in enumerate(notes):
        if note.get("is_rest"):
            continue
        lyric = note.get("lyric", "")
        if not lyric:
            continue

        syllabic = note.get("syllabic", SYLLABIC_SINGLE)
        fragment = NoteFragment(note_index=note_index, lyric=lyric, syllabic=syllabic)

        if syllabic == SYLLABIC_SINGLE:
            if current is not None:
                raise WordGroupingError(
                    "Note {0} ('{1}') is a single-syllable word, but a previous "
                    "word (opened with begin/middle) was never closed with "
                    "syllabic='end'.".format(note_index, lyric)
                )
            words.append(Word(text=lyric, fragments=[fragment]))
        elif syllabic == SYLLABIC_BEGIN:
            if current is not None:
                raise WordGroupingError(
                    "Note {0} ('{1}') opens a new word with syllabic='begin', "
                    "but a previous word was never closed with 'end'.".format(
                        note_index, lyric
                    )
                )
            current = [fragment]
        elif syllabic == SYLLABIC_MIDDLE:
            if current is None:
                raise WordGroupingError(
                    "Note {0} ('{1}') has syllabic='middle' but no word was "
                    "opened with 'begin' beforehand.".format(note_index, lyric)
                )
            current.append(fragment)
        elif syllabic == SYLLABIC_END:
            if current is None:
                raise WordGroupingError(
                    "Note {0} ('{1}') has syllabic='end' but no word was "
                    "opened with 'begin' beforehand.".format(note_index, lyric)
                )
            current.append(fragment)
            words.append(Word(text="".join(f.lyric for f in current), fragments=current))
            current = None
        else:
            raise WordGroupingError(
                "Note {0} ('{1}') has unknown syllabic value {2}.".format(
                    note_index, lyric, syllabic
                )
            )

    if current is not None:
        raise WordGroupingError(
            "Score ends with an unterminated word (notes {0}); the last "
            "syllable is missing syllabic='end'.".format(
                [f.note_index for f in current]
            )
        )

    return words
