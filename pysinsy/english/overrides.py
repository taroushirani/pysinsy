import os

_DEFAULT_OVERRIDES_PATH = os.path.join(
    os.path.dirname(__file__), "overrides", "default_overrides.tsv"
)


def _parse_tsv(path):
    overrides = {}
    with open(path, encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                raise ValueError(
                    "Malformed override entry at {0}:{1}: {2!r}".format(
                        path, lineno, line
                    )
                )
            word, syllables_str = parts
            syllables = [syl.split() for syl in syllables_str.split(".")]
            overrides[word.strip().lower()] = syllables
    return overrides


def load_overrides(overrides_path=None):
    """Load word -> list-of-syllables (each a list of ARPABET phonemes)
    overrides. Bundled defaults are loaded first, then `overrides_path` (if
    given) is merged on top and takes priority for any word it repeats."""
    overrides = _parse_tsv(_DEFAULT_OVERRIDES_PATH)
    if overrides_path:
        overrides.update(_parse_tsv(overrides_path))
    return overrides
