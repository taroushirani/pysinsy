#include "note_collector.h"

namespace pysinsy
{

NoteCollector::NoteCollector()
{
}

NoteCollector::~NoteCollector()
{
}

bool NoteCollector::setEncoding(const std::string& /*encoding*/)
{
   return true;
}

bool NoteCollector::addKeyMark(sinsy::ModeType /*modeType*/, int /*fifths*/)
{
   return true;
}

bool NoteCollector::addBeatMark(size_t /*beats*/, size_t /*beatType*/)
{
   return true;
}

bool NoteCollector::addTempoMark(double /*tempo*/)
{
   return true;
}

bool NoteCollector::addSuddenDynamicsMark(sinsy::SuddenDynamicsType /*suddenDynamicsType*/)
{
   return true;
}

bool NoteCollector::addGradualDynamicsMark(sinsy::GradualDynamicsType /*gradualDynamicsType*/)
{
   return true;
}

bool NoteCollector::addNote(size_t duration, const std::string& lyric, size_t /*pitch*/, bool /*accent*/,
                             bool /*staccato*/, sinsy::TieType /*tieType*/, sinsy::SlurType /*slurType*/,
                             sinsy::SyllabicType syllabicType, bool /*breath*/)
{
   notes.push_back(NoteRecord(lyric, syllabicType, duration, false));
   return true;
}

bool NoteCollector::addRest(size_t duration)
{
   notes.push_back(NoteRecord(std::string(), sinsy::SYLLABICTYPE_SINGLE, duration, true));
   return true;
}

const std::vector<NoteRecord>& NoteCollector::getNotes() const
{
   return notes;
}

};
