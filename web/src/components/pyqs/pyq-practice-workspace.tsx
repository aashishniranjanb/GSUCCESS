"use client";

import React from "react";
import { PYQDetailItem } from "@/lib/api/types";
import {
  UniversalQuestionPlayer,
  UniversalQuestionItem,
} from "@/components/study/universal-question-player";

interface PYQPracticeWorkspaceProps {
  question: PYQDetailItem;
  currentIndex: number;
  totalQuestions: number;
  onNext?: () => void;
  onPrevious?: () => void;
  onBackToList?: () => void;
}

export function PYQPracticeWorkspace({
  question,
  currentIndex,
  totalQuestions,
  onNext,
  onPrevious,
  onBackToList,
}: PYQPracticeWorkspaceProps) {
  // Map PYQDetailItem to UniversalQuestionItem
  const universalItem: UniversalQuestionItem = {
    id: question.id,
    concept_id: question.topic_id,
    concept_name: question.topic_name,
    topic_name: question.topic_name,
    question_text: question.question_text,
    options: question.options,
    difficulty: question.difficulty,
    provenance: question.provenance || `GPAT ${question.pyq_year}`,
    verification_status: question.verification_status,
    answer_status: question.answer_status,
    pyq_year: question.pyq_year,
    cognitive_level: question.cognitive_level,
    cue: question.cue,
    explanation: question.explanation,
    source_page: question.source_page,
    distractor_reasons: question.distractor_reasons,
  };

  return (
    <UniversalQuestionPlayer
      question={universalItem}
      currentIndex={currentIndex}
      totalQuestions={totalQuestions}
      sessionModeTag={`GPAT ${question.pyq_year} PYQ`}
      localCorrectOption={question.correct_option}
      onNext={onNext}
      onPrevious={onPrevious}
      isLast={currentIndex === totalQuestions - 1}
      onBackToList={onBackToList}
    />
  );
}
