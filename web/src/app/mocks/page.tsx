"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  fetchMockBlueprints,
  fetchMockHistory,
  createMockExam,
  startMockExam,
  fetchMockExam,
  submitMockExam,
  MockApiError,
} from "@/lib/api/mocks";
import {
  MockBlueprintItem,
  MockHistoryItem,
  MockExamSession,
  MockEvaluationResult,
  CreateMockOptions,
} from "@/lib/api/types";
import { MockSelector } from "@/components/mocks/mock-selector";
import { ActiveExamWorkspace } from "@/components/mocks/active-exam-workspace";
import { MockResultView } from "@/components/mocks/mock-result-view";
import { MiniMockBuilderModal } from "@/components/mocks/mini-mock-builder-modal";
import { ErrorState, Skeleton } from "@/components/ui/states";

type MockViewStage = "select" | "active" | "result";

export default function MocksPage() {
  const router = useRouter();
  const [stage, setStage] = useState<MockViewStage>("select");
  const [blueprints, setBlueprints] = useState<MockBlueprintItem[]>([]);
  const [history, setHistory] = useState<MockHistoryItem[]>([]);
  const [activeSession, setActiveSession] = useState<MockExamSession | null>(null);
  const [activeResult, setActiveResult] = useState<MockEvaluationResult | null>(null);
  const [isMiniMockModalOpen, setIsMiniMockModalOpen] = useState<boolean>(false);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Initial load: fetch blueprints and past history
  const loadInitialData = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const [bpRes, histRes] = await Promise.all([
        fetchMockBlueprints(),
        fetchMockHistory("student_01"),
      ]);
      setBlueprints(bpRes.blueprints || []);
      setHistory(histRes.history || []);
    } catch (err: unknown) {
      const msg = err instanceof MockApiError ? err.message : "Failed to load mock arena data.";
      setErrorMsg(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handler: Start new exam from blueprint
  const handleSelectBlueprint = async (blueprintId: string) => {
    setErrorMsg(null);
    try {
      const createRes = await createMockExam(blueprintId, "student_01");
      await startMockExam(createRes.exam_id, "student_01");
      const session = await fetchMockExam(createRes.exam_id, "student_01");
      setActiveSession(session);
      setStage("active");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to start mock session.";
      setErrorMsg(msg);
    }
  };

  // Handler: Resume in-progress exam
  const handleResumeExam = async (examId: string) => {
    setErrorMsg(null);
    try {
      const session = await fetchMockExam(examId, "student_01");
      setActiveSession(session);
      setStage("active");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to resume mock session.";
      setErrorMsg(msg);
    }
  };

  // Handler: View evaluated diagnostic results
  const handleViewResults = async (examId: string) => {
    setErrorMsg(null);
    try {
      const session = await fetchMockExam(examId, "student_01");
      if (session.result) {
        setActiveResult(session.result);
        setStage("result");
      } else {
        setErrorMsg("Diagnostic result not available for this exam.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to fetch exam result.";
      setErrorMsg(msg);
    }
  };

  // Handler: Authoritative final submission
  const handleFinishExam = async (examId: string) => {
    setErrorMsg(null);
    try {
      const evalResult = await submitMockExam(examId, "student_01");
      setActiveResult(evalResult);
      setActiveSession(null);
      setStage("result");
      // Refresh history in background
      fetchMockHistory("student_01").then((res) => setHistory(res.history || [])).catch(() => {});
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to submit and score exam.";
      setErrorMsg(msg);
      throw err;
    }
  };

  // Handler: Exit back to selector
  const handleExitToSelector = () => {
    setActiveSession(null);
    setActiveResult(null);
    setStage("select");
    loadInitialData();
  };

  if (isLoading && stage === "select") {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-4 w-96" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Skeleton className="h-48 rounded-lg" />
          <Skeleton className="h-48 rounded-lg" />
          <Skeleton className="h-48 rounded-lg" />
        </div>
      </div>
    );
  }

  if (errorMsg && stage === "select" && blueprints.length === 0) {
    return (
      <div className="max-w-md mx-auto py-12">
        <ErrorState
          title="Mock Arena Unavailable"
          message={errorMsg}
          onRetry={loadInitialData}
        />
      </div>
    );
  }

  // Handler: Start personalized mini mock
  const handleGenerateMiniMock = async (options: CreateMockOptions) => {
    setErrorMsg(null);
    try {
      const createRes = await createMockExam(options, "student_01");
      await startMockExam(createRes.exam_id, "student_01");
      const session = await fetchMockExam(createRes.exam_id, "student_01");
      setActiveSession(session);
      setStage("active");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to launch personalized mini mock.";
      setErrorMsg(msg);
      throw err;
    }
  };

  return (
    <div className="animate-enter">
      {stage === "select" && (
        <>
          <MockSelector
            blueprints={blueprints}
            history={history}
            isLoading={isLoading}
            onSelectBlueprint={handleSelectBlueprint}
            onOpenMiniMockBuilder={() => setIsMiniMockModalOpen(true)}
            onResumeExam={handleResumeExam}
            onViewResults={handleViewResults}
          />
          <MiniMockBuilderModal
            isOpen={isMiniMockModalOpen}
            onClose={() => setIsMiniMockModalOpen(false)}
            onGenerateMock={handleGenerateMiniMock}
            studentId="student_01"
          />
        </>
      )}

      {stage === "active" && activeSession && (
        <ActiveExamWorkspace
          initialSession={activeSession}
          onFinishExam={handleFinishExam}
          onExitExam={handleExitToSelector}
        />
      )}

      {stage === "result" && activeResult && (
        <MockResultView
          result={activeResult}
          onRetake={handleExitToSelector}
          onPracticeTopic={(conceptId) => router.push(`/study?concept=${encodeURIComponent(conceptId)}`)}
        />
      )}
    </div>
  );
}
