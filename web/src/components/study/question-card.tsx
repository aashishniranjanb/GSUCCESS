"use client";

import React from "react";
import {
  DailySessionQuestion,
  AttemptFeedbackResponse,
} from "@/lib/api/types";
import {
  UniversalQuestionPlayer,
  UniversalQuestionItem,
} from "./universal-question-player";

interface QuestionCardProps {
  question: DailySessionQuestion;
  index: number;
  total: number;
  studentId: string;
  onSubmitAnswer: (
    questionId: string,
    selectedOption: number,
    responseTimeSec: number,
    confidence: number
  ) => Promise<AttemptFeedbackResponse>;
  onNext: () => void;
  isLast: boolean;
}

export function QuestionCard({
  question,
  index,
  total,
  studentId,
  onSubmitAnswer,
  onNext,
  isLast,
}: QuestionCardProps) {
  // Map DailySessionQuestion to UniversalQuestionItem
  const universalItem: UniversalQuestionItem = {
    id: question.question_id,
    concept_id: question.concept_id,
    concept_name: question.concept_name,
    question_text: question.question_text,
    options: question.options,
    difficulty: question.difficulty,
    candidate_type: question.candidate_type,
    media_url: question.media_url,
    media_alt: question.media_alt,
    media_caption: question.media_caption,
    cue: question.cue,
    source_page: question.source_page,
    previously_answered: question.item_status === "answered",
    previous_is_correct: question.is_correct,
  };

  return (
    <UniversalQuestionPlayer
      question={universalItem}
      currentIndex={index}
      totalQuestions={total}
      sessionModeTag="Daily Mission"
      studentId={studentId}
      onSubmitAnswer={onSubmitAnswer}
      onNext={onNext}
      isLast={isLast}
    />
  );
}
