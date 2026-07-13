# coding: utf-8

from os.path import dirname, join

import pysinsy

DATA_DIR = dirname(__file__)


def test_pysinsy_frontend():
    # http://sinsy.sp.nitech.ac.jp/sample/song070_f00001_063.xml

    xml_path = join(DATA_DIR, "song070_f00001_063.xml")

    sinsy = pysinsy.sinsy.Sinsy()
    assert sinsy.setLanguages("j", pysinsy.get_default_dic_dir())
    assert sinsy.loadScoreFromMusicXML(xml_path)

    for is_mono in [True, False]:
        label = sinsy.createLabelData(is_mono, 1, 1)
        for line in label.getData():
            print(line)

    sinsy.clearScore()


def test_pysinsy_synthesize():
    xml_path = join(DATA_DIR, "song070_f00001_063.xml")

    sinsy = pysinsy.sinsy.Sinsy()
    assert sinsy.setLanguages("j", pysinsy.get_default_dic_dir())
    assert sinsy.loadScoreFromMusicXML(xml_path)
    assert sinsy.loadVoices(pysinsy.get_default_htsvoice())

    wav, sr = sinsy.synthesize()
    assert len(wav) > 0 and wav.max() > 0
    assert sr == 48000

    sinsy.clearScore()


def test_pysinsy_highlevel():
    xml_path = join(DATA_DIR, "song070_f00001_063.xml")

    for _ in range(3):
        wav, sr = pysinsy.synthesize(xml_path)
        assert len(wav) > 0 and wav.max() > 0
        assert sr == 48000


def test_extract_fullcontext():
    xml_path = join(DATA_DIR, "song070_f00001_063.xml")

    labels = pysinsy.extract_fullcontext(xml_path)
    assert isinstance(labels, list)
    assert len(labels) > 0
    for i in range(5):
        print(labels[i])


def test_breath_mark_near_rest():
    # breath_before_rest.xml has a breath mark on a note immediately
    # followed by a rest, and a breath mark attached directly to a rest.
    # Both should produce a "br" phoneme.
    xml_path = join(DATA_DIR, "breath_before_rest.xml")

    sinsy = pysinsy.sinsy.Sinsy()
    assert sinsy.setLanguages("j", pysinsy.get_default_dic_dir())
    assert sinsy.loadScoreFromMusicXML(xml_path)

    label = sinsy.createLabelData(True, 1, 1)
    phonemes = [line.split()[-1] for line in label.getData()]

    assert phonemes.count("br") == 2

    # breath mark on the note "a", which is immediately followed by a rest
    a_idx = phonemes.index("a")
    assert phonemes[a_idx + 1] == "br"

    # breath mark attached directly to a rest note
    rest_br_idx = phonemes.index("br", a_idx + 2)
    assert phonemes[rest_br_idx - 1] == "pau"

    sinsy.clearScore()
