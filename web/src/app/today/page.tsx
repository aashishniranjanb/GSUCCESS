"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  fetchStudyToday,
  submitStudyAttempt,
  completeStudyMission,
  StudyApiError,
} from "@/lib/api/study";
import { fetchReviewQueue } from "@/lib/api/review";
import { fetchStudentProgress } from "@/lib/api/progress";
import { fetchSyllabusTree } from "@/lib/api/syllabus";
import {
  DailySessionResponse,
  AttemptFeedbackResponse,
  SyllabusExamGroup,
  LearnerLocalPreferences,
} from "@/lib/api/types";
import { getLocalPreferences, saveLocalPreferences } from "@/lib/preferences";
import { QuestionCard } from "@/components/study/question-card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton, ErrorState } from "@/components/ui/states";
import { WifiSlash } from "@phosphor-icons/react";

import { ExamCountdownCard } from "@/components/today/exam-countdown-card";
import { FsrsReviewSummaryCard } from "@/components/today/fsrs-review-summary-card";
import {
  TwoStudyChoicesSection,
  StudyRecommendationOption,
} from "@/components/today/two-study-choices-section";
import { DailyHeroSection } from "@/components/today/daily-hero-section";
import { MyStudyPlanSection } from "@/components/today/my-study-plan-section";
import { StudyPlanItem } from "@/components/today/study-planning-section";
import { StudiedTodaySection, StudiedActivityItem } from "@/components/today/studied-today-section";
import { SyllabusSubjectExplorerPreview } from "@/components/today/syllabus-explorer-preview";

const STUDENT_ID = "student_01";
const STORAGE_INDEX_KEY = `gpat_mission_index_${STUDENT_ID}`;
const STORAGE_PLAN_KEY = "gpat_learner_study_plan_v1";

export default function TodayPage() {
  const [session, setSession] = useState<DailySessionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(false);
  const [isExamModeActive, setIsExamModeActive] = useState<boolean>(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [isSessionCompleted, setIsSessionCompleted] = useState<boolean>(false);

  // Home Screen Telemetry & Data State
  const [dueCardsCount, setDueCardsCount] = useState<number>(0);
  const [dueCardsLoading, setDueCardsLoading] = useState<boolean>(true);
  const [todayActivities, setTodayActivities] = useState<StudiedActivityItem[]>([]);
  const [examGroups, setExamGroups] = useState<SyllabusExamGroup[]>([]);
  const [localPrefs, setLocalPrefs] = useState<LearnerLocalPreferences>(() => getLocalPreferences());
  const [planItems, setPlanItems] = useState<StudyPlanItem[]>([]);

  // Load study plan from durable local storage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_PLAN_KEY);
      if (raw) {
        setPlanItems(JSON.parse(raw));
      } else {
        const starter: StudyPlanItem[] = [
          {
            id: "plan_init_01",
            topicId: "pharmacology__ans__pd_antagonism",
            topicTitle: "Pharmacology: Receptor Antagonism & Competitive Kinetics",
            subjectId: "pharmacology",
            estimatedMinutes: 15,
            isCompleted: false,
            addedAt: new Date().toISOString(),
          },
          {
            id: "plan_init_02",
            topicId: "pharmaceutics__pharmaceutics__pharmaceuticals_and_dosage_forms",
            topicTitle: "Pharmaceutics: Dissolution Testing & BCS Classification",
            subjectId: "pharmaceutics",
            estimatedMinutes: 20,
            isCompleted: false,
            addedAt: new Date().toISOString(),
          },
        ];
        setPlanItems(starter);
        localStorage.setItem(STORAGE_PLAN_KEY, JSON.stringify(starter));
      }
    } catch {
      // quota or private mode fallback
    }
  }, []);

  const savePlanItems = (items: StudyPlanItem[]) => {
    setPlanItems(items);
    try {
      localStorage.setItem(STORAGE_PLAN_KEY, JSON.stringify(items));
    } catch {
      // quota handling
    }
  };

  const handleTogglePlanItem = (id: string) => {
    const updated = planItems.map((item) =>
      item.id === id ? { ...item, isCompleted: !item.isCompleted } : item
    );
    savePlanItems(updated);
  };

  const handleRemovePlanItem = (id: string) => {
    const updated = planItems.filter((item) => item.id !== id);
    savePlanItems(updated);
  };

  const handleAddPlanItem = (
    topicTitle: string,
    subjectId: string,
    durationMin: number,
    topicId?: string
  ) => {
    const newItem: StudyPlanItem = {
      id: `plan_${Date.now()}`,
      topicId: topicId || topicTitle.toLowerCase().replace(/\s+/g, "_"),
      topicTitle,
      subjectId,
      estimatedMinutes: durationMin,
      isCompleted: false,
      addedAt: new Date().toISOString(),
    };
    savePlanItems([...planItems, newItem]);
  };

  const handleReorderPlanItems = (reordered: StudyPlanItem[]) => {
    savePlanItems(reordered);
  };

  // Monitor network status
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Fetch session data from FastAPI
  const loadDailySession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStudyToday(STUDENT_ID, 12, "balanced");
      setSession(data);

      let initialIdx = data.next_pending_index || 0;
      if (typeof window !== "undefined") {
        const saved = localStorage.getItem(STORAGE_INDEX_KEY);
        if (saved !== null) {
          const parsed = parseInt(saved, 10);
          if (!isNaN(parsed) && parsed >= 0 && parsed < data.questions.length) {
            initialIdx = parsed;
          }
        }
      }
      setCurrentQuestionIndex(initialIdx);

      if (data.is_completed || data.status === "completed") {
        setIsSessionCompleted(true);
      }
    } catch (err: unknown) {
      if (err instanceof StudyApiError && err.status === 0) {
        setIsOffline(true);
      }
      const msg = err instanceof Error ? err.message : "Failed to load today's study mission.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch auxiliary data for home widgets
  const loadHomeWidgetsData = useCallback(async () => {
    // 1. FSRS Review Queue
    setDueCardsLoading(true);
    try {
      const reviewData = await fetchReviewQueue(STUDENT_ID);
      setDueCardsCount(reviewData.due_count || 0);
    } catch (e) {
      console.warn("Could not load review queue for home:", e);
    } finally {
      setDueCardsLoading(false);
    }

    // 2. Syllabus Tree
    try {
      const treeData = await fetchSyllabusTree();
      setExamGroups(treeData.tree || []);
    } catch (e) {
      console.warn("Could not load syllabus tree preview:", e);
    }

    // 3. Learner Progress & Today's Activity
    try {
      const progressData = await fetchStudentProgress(STUDENT_ID);
      const todayIso = new Date().toISOString().split("T")[0];
      const todayActivity = progressData.daily_activity.find((d) => d.date === todayIso);

      if (todayActivity && todayActivity.attempts > 0) {
        const items: StudiedActivityItem[] = Array.from({
          length: todayActivity.attempts,
        }).map((_, idx) => ({
          id: `act_today_${idx}`,
          type: "mission_answered",
          title: `Daily Practice: Question #${idx + 1} Answered`,
          isCorrect: idx < todayActivity.correct,
          timeSpentSec: Math.round(todayActivity.avg_time_sec) || 35,
          timestamp: new Date().toISOString(),
        }));
        setTodayActivities(items);
      } else {
        setTodayActivities([]);
      }
    } catch (e) {
      console.warn("Could not load progress activity for home:", e);
    }
  }, []);

  useEffect(() => {
    void loadDailySession();
    void loadHomeWidgetsData();
    setLocalPrefs(getLocalPreferences());
  }, [loadDailySession, loadHomeWidgetsData]);

  // Persist index changes locally for seamless resumption
  const handleIndexChange = (newIdx: number) => {
    setCurrentQuestionIndex(newIdx);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_INDEX_KEY, newIdx.toString());
    }
  };

  const handleStartMission = () => {
    setIsExamModeActive(true);
  };

  const handleUpdateTargetDate = (newDate: string | null, label?: string | null) => {
    const updated = saveLocalPreferences({
      targetExamDate: newDate,
      targetExamLabel: label || null,
    });
    setLocalPrefs(updated);
  };

  const handleSubmitAnswer = async (
    questionId: string,
    selectedOption: number,
    responseTimeSec: number,
    confidence: number
  ): Promise<AttemptFeedbackResponse> => {
    const feedback = await submitStudyAttempt({
      student_id: STUDENT_ID,
      question_id: questionId,
      selected_option: selectedOption,
      response_time_sec: responseTimeSec,
      confidence: confidence,
    });

    if (session) {
      const updatedQuestions = session.questions.map((q) => {
        if (q.question_id === questionId) {
          return {
            ...q,
            item_status: "answered" as const,
            is_correct: feedback.is_correct,
          };
        }
        return q;
      });

      const newAnsweredCount = session.answered_count + 1;
      const newPendingCount = Math.max(0, session.pending_count - 1);

      setSession({
        ...session,
        questions: updatedQuestions,
        answered_count: newAnsweredCount,
        pending_count: newPendingCount,
      });

      setTodayActivities((prev) => [
        {
          id: `act_${Date.now()}`,
          type: "mission_answered",
          title: `Question Attempt: ${feedback.is_correct ? "Correct Recall" : "Review Required"}`,
          isCorrect: feedback.is_correct,
          timeSpentSec: Math.round(responseTimeSec),
          timestamp: new Date().toISOString(),
        },
        ...prev,
      ]);
    }

    return feedback;
  };

  const handleNextQuestion = async () => {
    if (!session) return;

    if (currentQuestionIndex + 1 < session.questions.length) {
      handleIndexChange(currentQuestionIndex + 1);
    } else {
      setIsSessionCompleted(true);
      setIsExamModeActive(false);
      try {
        await completeStudyMission(session.session_id);
      } catch (e) {
        console.warn("Could not mark session complete on server:", e);
      }
      if (typeof window !== "undefined") {
        localStorage.removeItem(STORAGE_INDEX_KEY);
      }
    }
  };

  // Construct Dynamic Recommendation Options A & B based on real data
  const optionA: StudyRecommendationOption = {
    optionKey: "A",
    subjectId: "pharmacology",
    subjectName: "Pharmacology & Allied Subjects",
    topicTitle: session?.headline || "Autonomic nervous system",
    unitTitle: "Adrenergic & Cholinergic Pharmacology",
    estimatedMinutes: session?.estimated_duration_minutes || 12,
    whyRecommended:
      session?.why_this_mission ||
      "Balances high-yield examination weightage with active recall questions.",
    targetQuestionCount: session?.target_question_count || 8,
    dueCardsCount: dueCardsCount,
    topicId: "pharmacology__ans__pd_antagonism",
    mode: "balanced",
  };

  const optionB: StudyRecommendationOption = {
    optionKey: "B",
    subjectId: "pharmaceutics",
    subjectName: "Pharmaceutics & Allied Subjects",
    topicTitle: "Dissolution & drug release",
    unitTitle: "Physical Pharmaceutics & Biopharmaceutics",
    estimatedMinutes: 12,
    whyRecommended:
      "Core formulation concept frequently tested in official GPAT papers.",
    targetQuestionCount: 8,
    topicId: "pharmaceutics__pharmaceutics__pharmaceuticals_and_dosage_forms",
    mode: "repair",
  };

  // --- Render Loading State ---
  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-2 animate-enter">
        <div className="space-y-2">
          <Skeleton className="h-7 w-48" />
          <Skeleton className="h-4 w-72" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-40 rounded-xl" />
          <Skeleton className="h-40 rounded-xl" />
        </div>
        <Skeleton className="h-56 rounded-xl" />
      </div>
    );
  }

  // --- Render Error / Offline Fallback ---
  if (error && !session) {
    return (
      <div className="space-y-6 max-w-xl mx-auto py-12 animate-enter">
        <ErrorState
          title={isOffline ? "Offline Mode" : "Failed to Load Daily Home"}
          message={
            isOffline
              ? "Cannot connect to the learning server. Please ensure FastAPI is running on http://localhost:8000."
              : error
          }
          onRetry={loadDailySession}
        />
      </div>
    );
  }

  // --- Render Active Learning Flow (Interactive Question Card) ---
  if (isExamModeActive && session && !isSessionCompleted) {
    const currentQuestion = session.questions[currentQuestionIndex];

    return (
      <div className="space-y-6 max-w-3xl mx-auto animate-enter">
        <div className="flex items-center justify-between pb-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center gap-2">
            <Badge variant="primary" className="font-mono text-[10px]">
              Daily Mission
            </Badge>
            <span className="text-xs font-mono text-[var(--color-text-secondary)]">
              Question {currentQuestionIndex + 1} of {session.questions.length}
            </span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExamModeActive(false)}
            className="text-xs"
          >
            Exit to Daily Home
          </Button>
        </div>

        <QuestionCard
          question={currentQuestion}
          index={currentQuestionIndex}
          total={session.questions.length}
          studentId={STUDENT_ID}
          onSubmitAnswer={handleSubmitAnswer}
          onNext={handleNextQuestion}
          isLast={currentQuestionIndex === session.questions.length - 1}
        />
      </div>
    );
  }

  // --- Check if mission is in progress ---
  const answeredCount = session?.answered_count ?? 0;
  const totalQuestions = session?.questions.length ?? 8;
  const isMissionInProgress = answeredCount > 0 && answeredCount < totalQuestions;

  // --- Render Canonical Daily Home Workspace ---
  return (
    <div className="space-y-6 max-w-5xl mx-auto py-1 animate-enter">
      {/* Offline Alert Bar */}
      {isOffline && (
        <div
          role="status"
          className="p-3 rounded-lg bg-[rgb(252_211_77/0.1)] border border-[var(--color-status-warning)]/30 text-xs text-[var(--color-status-warning)] flex items-center gap-2"
        >
          <WifiSlash size={16} weight="bold" />
          <span>Offline mode: Cached study home active. Responses will queue locally.</span>
        </div>
      )}

      {/* Section 2 & 3: Personalized Greeting, Botanical Hero & Daily Mission Action */}
      <DailyHeroSection
        headline={session?.headline || "Establish your baseline."}
        supportingText={
          session?.why_this_mission ||
          "Balances high-yield examination weightage with active recall questions."
        }
        estimatedMinutes={session?.estimated_duration_minutes || 12}
        isCompleted={isSessionCompleted}
        isMissionInProgress={isMissionInProgress}
        answeredCount={answeredCount}
        totalQuestions={totalQuestions}
        onStartMission={handleStartMission}
        learnerName={localPrefs.learnerName}
      />

      {/* Section 4 & 6: Compact Study Status (Target Exam Date & Essential Review) */}
      <section className="grid grid-cols-1 sm:grid-cols-2 gap-4" aria-label="Key Exam Metrics and Reviews">
        <ExamCountdownCard
          targetDate={localPrefs.targetExamDate}
          targetLabel={localPrefs.targetExamLabel}
          onUpdateTargetDate={handleUpdateTargetDate}
        />

        <FsrsReviewSummaryCard
          dueCount={dueCardsCount}
          isLoading={dueCardsLoading}
        />
      </section>

      {/* Section 5: Two Recommended Study Choices (Option A & Option B) */}
      <TwoStudyChoicesSection
        optionA={optionA}
        optionB={optionB}
        isStarting={false}
        onSelectOption={() => handleStartMission()}
      />

      {/* Section 7: Learner-Controlled My Study Plan */}
      <MyStudyPlanSection
        planItems={planItems}
        onTogglePlanItem={handleTogglePlanItem}
        onRemovePlanItem={handleRemovePlanItem}
        onAddPlanItem={handleAddPlanItem}
        onReorderPlanItems={handleReorderPlanItems}
        examGroups={examGroups}
      />

      {/* Section 8: Studied Today / Recent Activity */}
      <section aria-label="Studied Today Activity History">
        <StudiedTodaySection
          activities={todayActivities}
          isLoading={false}
        />
      </section>

      {/* Section 9: Explore by Subject */}
      <SyllabusSubjectExplorerPreview
        examGroups={examGroups}
      />
    </div>
  );
}
