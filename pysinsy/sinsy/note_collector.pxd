# distutils: language = c++

from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector

from .sinsy cimport IScore


cdef extern from "note_collector.h" namespace "pysinsy":
    cdef cppclass NoteRecord:
        string lyric
        size_t syllabic
        size_t duration
        bool isRest

    cdef cppclass NoteCollector(IScore):
        NoteCollector()
        const vector[NoteRecord]& getNotes()
