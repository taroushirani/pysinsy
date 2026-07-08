import re

_PHONEME_RE = re.compile(r"^[A-Z]+[0-2]?$")

_g2p = None


def _get_g2p():
    global _g2p
    if _g2p is None:
        try:
            from g2p_en import G2p
        except ImportError as e:
            raise ImportError(
                "g2p_en is required for English lyric-to-phoneme conversion. "
                "Install it with: pip install pysinsy[english]"
            ) from e
        _g2p = G2p()
    return _g2p


def word_to_phonemes(word):
    """Convert an English word to a flat ARPABET phoneme sequence (stress
    digits included, no syllable-boundary information)."""
    g2p = _get_g2p()
    return [p for p in g2p(word) if _PHONEME_RE.match(p)]
