#ifndef PYSINSY_NOTE_COLLECTOR_H_
#define PYSINSY_NOTE_COLLECTOR_H_

#include <string>
#include <vector>

#include "sinsy.h"

namespace pysinsy
{

struct NoteRecord
{
   std::string lyric;
   size_t syllabic;
   size_t duration;
   bool isRest;

   NoteRecord() : syllabic(0), duration(0), isRest(false) {
   }

   NoteRecord(const std::string& lyric_, size_t syllabic_, size_t duration_, bool isRest_) :
      lyric(lyric_), syllabic(syllabic_), duration(duration_), isRest(isRest_) {
   }
};

//! Collects the notes of a loaded score via sinsy::Sinsy::toScore(), so they
//! can be read back from Python (word/syllable reconstruction for English lyrics).
class NoteCollector : public sinsy::IScore
{
public:
   NoteCollector();
   virtual ~NoteCollector();

   virtual bool setEncoding(const std::string& encoding);
   virtual bool addKeyMark(sinsy::ModeType modeType, int fifths);
   virtual bool addBeatMark(size_t beats, size_t beatType);
   virtual bool addTempoMark(double tempo);
   virtual bool addSuddenDynamicsMark(sinsy::SuddenDynamicsType suddenDynamicsType);
   virtual bool addGradualDynamicsMark(sinsy::GradualDynamicsType gradualDynamicsType);
   virtual bool addNote(size_t duration, const std::string& lyric, size_t pitch, bool accent, bool staccato,
                         sinsy::TieType tieType, sinsy::SlurType slurType, sinsy::SyllabicType syllabicType,
                         bool breath = false);
   virtual bool addRest(size_t duration);

   const std::vector<NoteRecord>& getNotes() const;

private:
   //! copy constructor (do not use)
   NoteCollector(const NoteCollector&);

   //! assignment operator (do not use)
   NoteCollector& operator=(const NoteCollector&);

   std::vector<NoteRecord> notes;
};

};

#endif // PYSINSY_NOTE_COLLECTOR_H_
