export interface DailySessionQuestion {
  question_id: string;
  concept_id: string;
  concept_name?: string;
  question_type: string;
  candidate_type?: string;
  reason_codes?: string[];
  difficulty: number;
  importance?: number;
  question_text: string;
  options: string[];
  source_page?: number;
  cue?: string | null;
  media_url?: string | null;
  media_alt?: string | null;
  media_caption?: string | null;
  priority_score?: number;
  is_due?: boolean;
  has_active_misconception?: boolean;
  estimated_seconds?: number;
  item_status?: "pending" | "answered";
  is_correct?: boolean;
}

export interface SessionTimelineBlock {
  block: string;
  duration_min: number;
}

export interface SessionComposition {
  due_recall_count: number;
  misconception_repair_count: number;
  high_yield_concept_count: number;
}

export interface DailySessionResponse {
  session_id: string;
  mission_id: string;
  session_time_minutes: number;
  estimated_duration_minutes: number;
  target_question_count: number;
  mode: string;
  status: "active" | "completed";
  headline: string;
  explanation: string;
  why_this_mission: string;
  answered_count: number;
  pending_count: number;
  next_pending_index: number;
  is_resumable: boolean;
  is_completed: boolean;
  composition?: SessionComposition;
  timeline?: SessionTimelineBlock[];
  questions: DailySessionQuestion[];
}

export interface AttemptSubmissionRequest {
  student_id: string;
  question_id: string;
  selected_option: number;
  response_time_sec: number;
  confidence: number;
  hint_used?: number;
}

export interface AttemptFeedbackResponse {
  is_correct: boolean;
  selected_option: number;
  correct_option: number;
  explanation: string;
  distractor_reason?: string | null;
  calibration_category?: string;
  error_type?: string | null;
  source_page?: number;
  cue?: string | null;
  fsrs_rating?: string;
  next_due_date?: string;
  concept_mastery?: number;
  stability_days?: number;
  new_achievements?: unknown[];
}

// --- Phase 3A: Canonical Syllabus Explorer Types ---

export interface SyllabusTopicSummary {
  topic_id: string;
  name: string;
  subject_id: string;
  curriculum_subject_id: string;
  unit_id: string;
  question_count: number;
  objective_count?: number;
  flashcard_count?: number;
  is_verified?: boolean;
}

export interface SyllabusCurriculumSubject {
  curriculum_subject_id: string;
  exam_subject_id: string;
  name: string;
  pci_course_code?: string;
  semester_recommended?: number;
  description?: string;
  units?: SyllabusUnitSummary[];
  unit_count?: number;
  topics: SyllabusTopicSummary[];
  topic_count: number;
  total_questions: number;
}

export interface SyllabusExamGroup {
  exam_subject_id: string;
  name: string;
  curriculum_subjects: SyllabusCurriculumSubject[];
  curriculum_count: number;
  total_topics: number;
  total_questions: number;
}

export interface SyllabusVersion {
  version_id: string;
  authority_name: string;
  title: string;
  effective_year: number;
  status: string;
}

export interface SyllabusUnitSummary {
  unit_id: string;
  curriculum_subject_id: string;
  unit_number: number;
  title: string;
}

export interface SyllabusTreeResponse {
  syllabus_versions?: SyllabusVersion[];
  total_exam_groups: number;
  total_curriculum_courses?: number;
  total_units?: number;
  total_topics?: number;
  total_verified_topics?: number;
  total_needs_review_topics?: number;
  tree: SyllabusExamGroup[];
}

export interface TopicMetadata {
  topic_id: string;
  name: string;
  subject_id: string;
  curriculum_subject_id: string;
  unit_id: string;
  extraction_status?: string;
  verification_status?: string;
  curriculum_name?: string;
  pci_course_code?: string;
  semester_recommended?: number;
  exam_subject_name?: string;
  unit_number?: number;
  unit_title?: string;
}

export interface TopicContentChunk {
  chunk_id: string;
  source_id: string;
  page_or_range?: string;
  heading_path?: string;
  content: string;
  content_type?: string;
}

export interface TopicQuestion {
  id: string;
  pyq_year?: number;
  question_text: string;
  options?: string[];
  correct_option?: number;
  difficulty?: number;
  cognitive_level?: string;
  verification_status?: string;
  paper_id?: string;
  media_id?: string;
  media_url?: string | null;
  media_alt?: string | null;
  media_caption?: string | null;
  cue?: string | null;
  explanation?: string | null;
  source_page?: number | null;
  distractor_reasons?: Record<string, string>;
  provenance?: string;
}

export interface TopicLearningObjective {
  objective_id: string;
  code?: string;
  bloom_level?: string;
  objective_statement: string;
  key_formula_or_rule?: string;
  clinical_pearl?: string;
}

export interface TopicFlashcard {
  card_id: string;
  front: string;
  back: string;
  explanation?: string;
  difficulty?: number;
  importance?: number;
}

export interface TopicMediaItem {
  media_id: string;
  media_type: string;
  relative_file_path: string;
  alt_text?: string;
  caption?: string;
  source_id?: string;
  page_number?: number;
  rights_status?: string;
}

export interface ContentSourceItem {
  source_id: string;
  title: string;
  authority_category: string;
  conversion_tool?: string;
  page_count_estimate?: number;
}

export interface TopicDetailResponse {
  topic: TopicMetadata;
  content_chunks: TopicContentChunk[];
  questions: TopicQuestion[];
  learning_objectives: TopicLearningObjective[];
  flashcards: TopicFlashcard[];
  media?: TopicMediaItem[];
  sources?: ContentSourceItem[];
  chunk_count: number;
  question_count: number;
  objective_count: number;
  flashcard_count: number;
  media_count?: number;
}

// --- Phase 3B: PYQ Explorer & Practice Types ---

export interface PYQYearItem {
  year: number;
  question_count: number;
  quarantined_count: number;
  status: string;
  paper_id: string;
}

export interface PYQListItem {
  id: string;
  pyq_year: number;
  paper_id?: string;
  question_type: string;
  cognitive_level?: string;
  difficulty?: number;
  question_text: string;
  options: string[];
  cue?: string | null;
  source_page?: number;
  provenance: string;
  verification_status: string;
  answer_status?: string;
  topic_id?: string;
  topic_name: string;
  subject_id?: string;
  is_mapped: boolean;
}

export interface PYQListResponse {
  total_count: number;
  page: number;
  page_size: number;
  questions: PYQListItem[];
}

export interface PYQDetailItem extends PYQListItem {
  correct_option: number;
  distractor_reasons?: Record<string, string>;
  explanation?: string;
}

// --- Phase 3C: FSRS Spaced Repetition Review Types ---

export interface ReviewQueueCard {
  card_id: number;
  question_id: string;
  concept_id: string;
  concept_name: string;
  due: string;
  stability_days: number;
  step: number;
  state: number;
  question_text: string;
  options: string[];
  correct_option: number;
  explanation: string;
  cue?: string | null;
}

export interface ReviewQueueResponse {
  student_id: string;
  due_count: number;
  review_items: ReviewQueueCard[];
}

export type FSRSRating = "Again" | "Hard" | "Good" | "Easy";

export interface ReviewRatingRequest {
  student_id: string;
  card_id?: number | null;
  question_id: string;
  rating: FSRSRating;
  response_time_sec?: number;
}

export interface ReviewRatingResponse {
  status: string;
  card_id: number;
  question_id: string;
  rating: string;
  state: number;
  stability_days: number;
  difficulty: number;
  due: string;
  explanation: string;
}

// --- Phase 3D: Mock Exam & Diagnostic Types ---

export interface MockBlueprintItem {
  id: string;
  name: string;
  title: string;
  exam_version: "PROVISIONAL_MOCK" | "OFFICIAL_EXAM_SIMULATION";
  total_questions: number;
  duration_minutes: number;
  duration_seconds: number;
  marks_per_question: number;
  negative_marks: number;
  difficulty_distribution?: Record<string, number>;
  description?: string;
}

export interface MockBlueprintsResponse {
  blueprints: MockBlueprintItem[];
}

export interface MockCreateResponse {
  exam_id: string;
  title: string;
  exam_version: string;
  status: string;
  total_questions: number;
  duration_seconds: number;
  marks_per_question: number;
  negative_marks: number;
}

export interface CreateMockOptions {
  blueprintName?: string;
  userId?: string;
  customTitle?: string;
  questionCount?: number;
  durationMinutes?: number;
  topicIds?: string[];
  subjectIds?: string[];
}

export interface MiniMockConceptBreakdown {
  concept_id: string;
  concept_name: string;
  domain_id: string;
  eligible_count: number;
}

export interface MiniMockConceptOption {
  concept_id: string;
  name: string;
  question_count: number;
}

export interface MiniMockDomainOption {
  domain_id: string;
  display_name: string;
  total_questions: number;
  concepts: MiniMockConceptOption[];
}

export interface MiniMockCoverageResponse {
  requested_count: number;
  eligible_count: number;
  achievable_count: number;
  is_achievable: boolean;
  coverage_gaps: string[];
  concepts_breakdown: MiniMockConceptBreakdown[];
  available_domains?: MiniMockDomainOption[];
  estimated_duration_minutes: number;
  marking_scheme: {
    correct_marks: number;
    negative_marks: number;
    unattempted_marks: number;
    rule: string;
  };
}

export interface MockQuestionItem {
  position: number;
  question_id: string;
  concept_id: string;
  concept_name: string;
  domain_id: string;
  question_type: string;
  difficulty: number;
  question_text: string;
  options: string[];
  marks: number;
  negative_marks: number;
  selected_option: number | null;
  confidence: number | null;
}

export interface MockScorerSummary {
  total_questions: number;
  attempted: number;
  unattempted: number;
  correct: number;
  incorrect: number;
  raw_score: number;
  max_possible_score: number;
  score_percent: number;
  accuracy_percent: number;
  total_time_sec: number;
  avg_time_per_q_sec: number;
}

export interface MockTimingQuadrants {
  fast_correct: number;
  slow_correct: number;
  fast_incorrect: number;
  slow_incorrect: number;
}

export interface MockConceptPerformance {
  concept_id: string;
  name: string;
  total: number;
  correct: number;
  accuracy: number;
  tier: "STRONG" | "FRAGILE" | "WEAK";
  score: number;
}

export interface MockIdentifiedTrap {
  question_id: string;
  concept_id: string;
  concept_name: string;
  selected_option: number;
  distractor_reason: string;
  confidence: number;
  time_spent_sec: number;
}

export interface MockRecommendedRepair {
  concept_id: string;
  concept_name: string;
  reason: string;
  recommended_mode: "repair" | "review";
}

export interface MockEvaluationResult {
  exam_id?: string;
  status?: string;
  summary: MockScorerSummary;
  timing_analysis: {
    quadrants: MockTimingQuadrants;
    interpretation: {
      automated_retrieval_rate: number;
      inefficient_retrieval_rate: number;
      careless_error_rate: number;
      deep_struggle_rate: number;
    };
  };
  confidence_calibration?: {
    high_conf_correct: number;
    low_conf_correct: number;
    high_conf_incorrect: number;
    low_conf_incorrect: number;
  };
  domain_performance?: Record<string, { total: number; correct: number; incorrect: number; unattempted: number; score: number }>;
  concept_performance?: MockConceptPerformance[];
  question_type_performance?: Record<string, { total: number; correct: number; incorrect: number; score: number }>;
  identified_traps?: MockIdentifiedTrap[];
  recommended_repairs?: MockRecommendedRepair[];
}

export interface MockExamSession {
  exam_id: string;
  title: string;
  exam_version: string;
  status: "CREATED" | "READY" | "STARTED" | "IN_PROGRESS" | "PAUSED" | "SUBMITTED" | "EVALUATED";
  duration_seconds: number;
  elapsed_seconds: number;
  remaining_seconds: number;
  total_questions: number;
  marks_per_question: number;
  negative_marks: number;
  questions: MockQuestionItem[];
  result?: MockEvaluationResult | null;
}

export interface MockHistoryItem {
  id: string;
  title: string;
  exam_version: string;
  blueprint_name: string;
  duration_seconds: number;
  total_questions: number;
  status: string;
  score: number | null;
  score_percent: number | null;
  accuracy_percent: number | null;
  started_at: string | null;
  submitted_at: string | null;
  created_at: string;
}

// --- Phase 3E: Progress & Learning Analytics Types ---

export interface ProgressSummary {
  total_concepts: number;
  mastered_concepts: number;
  total_attempts: number;
  total_correct: number;
  total_incorrect: number;
  overall_accuracy_percent: number;
  completed_sessions: number;
  latest_activity_date: string | null;
  active_misconceptions: number;
  repaired_misconceptions: number;
  recurring_misconceptions: number;
  active_study_days: number;
  status: string;
}

export interface ProgressDailyActivity {
  date: string;
  attempts: number;
  correct: number;
  incorrect: number;
  accuracy_percent: number;
  avg_time_sec: number;
}

export interface ProgressFSRSWorkload {
  due_reviews: number;
  overdue_reviews: number;
  total_cards: number;
  learning_cards: number;
  review_cards: number;
  forecast_3_days: number;
  forecast_7_days: number;
  forecast_14_days: number;
}

export interface ProgressDomainPerformance {
  domain_id: string;
  attempts: number;
  correct: number;
  incorrect: number;
  accuracy_percent: number;
}

export interface ProgressSyllabusCoverage {
  domain_id: string;
  total_concepts: number;
  assessed_concepts: number;
  unassessed_concepts: number;
  coverage_percent: number;
  attempts: number;
  correct: number;
}

export interface ProgressMockHistoryItem {
  id: string;
  title: string;
  blueprint_name: string;
  total_questions: number;
  score: number;
  score_percent: number;
  accuracy_percent: number;
  submitted_at: string;
  result?: MockEvaluationResult | null;
}

export interface ProgressActiveTrap {
  id: number;
  concept_id: string;
  concept_name: string;
  question_id: string;
  distractor_reason: string;
  error_type: string;
  occurrence_count: number;
  status: string;
}

export interface ProgressRecommendedAction {
  type: "review" | "repair" | "practice" | "explore" | "mission" | "mock";
  title: string;
  description: string;
  cta_label: string;
  cta_href: string;
  rationale?: string;
}

export interface ProgressConceptItem {
  id: string;
  name: string;
  domain_id: string;
  importance_score: number;
  mastery: number;
  mastery_state: "UNASSESSED" | "LEARNING" | "RETAINING" | "DEMONSTRATED_MASTERY" | "NEEDS_REPAIR";
  stability_days: number;
  retrievability: number;
  attempts: number;
  correct: number;
  misconception_count: number;
  last_review: string | null;
  next_review: string | null;
}

export interface StudentProgressResponse {
  student_id: string;
  summary: ProgressSummary;
  daily_activity: ProgressDailyActivity[];
  fsrs_workload: ProgressFSRSWorkload;
  domain_performance: ProgressDomainPerformance[];
  syllabus_coverage?: ProgressSyllabusCoverage[];
  active_traps: ProgressActiveTrap[];
  recommended_next_action: ProgressRecommendedAction;
  mock_history?: ProgressMockHistoryItem[];
  concepts: ProgressConceptItem[];
}

// --- Phase 3F: Settings, Account & Learner Preferences Types ---

export interface WeeklyStudyGoal {
  goal_type: string;
  target_count: number;
  achieved_count: number;
  is_met: boolean;
  status: string;
  week_range: string;
  iso_week: string;
}

export interface LearnerRewardsResponse {
  student_id: string;
  weekly_goal: WeeklyStudyGoal;
  counts: {
    mission_completed: number;
    delayed_recall: number;
    misconception_repaired: number;
    topic_mastery: number;
    personal_best: number;
    total_awarded: number;
  };
  achievements: Array<{
    id: string;
    achievement_type: string;
    title: string;
    description: string;
    awarded_at: string;
  }>;
}

export interface LearnerLocalPreferences {
  preferredMissionDurationMinutes: number;
  preferredReviewBatchSize: number;
  reducedMotion: boolean;
  theme: "dark" | "light" | "warm-editorial";
  notificationsEnabled: boolean;
  reminderTime: string | null;
  targetExamDate: string | null;
  targetExamLabel: string | null;
  learnerName?: string | null;
}



