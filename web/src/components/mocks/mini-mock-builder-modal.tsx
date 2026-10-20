"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  MiniMockCoverageResponse,
  MiniMockDomainOption,
  CreateMockOptions,
} from "@/lib/api/types";
import { fetchMiniMockCoverage } from "@/lib/api/mocks";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  X,
  WarningCircle,
  SlidersHorizontal,
  Clock,
  Sparkle,
  ArrowRight,
  ArrowLeft,
  Check,
  ShieldCheck,
} from "@phosphor-icons/react/dist/ssr";

interface MiniMockBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerateMock: (options: CreateMockOptions) => Promise<void>;
  studentId?: string;
}

const PAPER_SIZES = [
  { count: 10, label: "10 Questions", tag: "Quick Check", durationMin: 18 },
  { count: 25, label: "25 Questions", tag: "Standard Sprint", durationMin: 45 },
  { count: 40, label: "40 Questions", tag: "Sectional Mock", durationMin: 72 },
];

export function MiniMockBuilderModal({
  isOpen,
  onClose,
  onGenerateMock,
  studentId = "student_01",
}: MiniMockBuilderModalProps) {
  // Wizard steps: 1 = Scope Selection, 2 = Paper Size & Blueprint, 3 = Blueprint Review & Generation
  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Selections
  const [selectedDomainIds, setSelectedDomainIds] = useState<Set<string>>(new Set());
  const [selectedConceptIds, setSelectedConceptIds] = useState<Set<string>>(new Set());
  const [questionCount, setQuestionCount] = useState<number>(10);
  const [customTitle, setCustomTitle] = useState<string>("");

  // Coverage and domain metadata from backend
  const [coverageData, setCoverageData] = useState<MiniMockCoverageResponse | null>(null);
  const [isLoadingCoverage, setIsLoadingCoverage] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Available domains cache from first coverage response
  const [availableDomains, setAvailableDomains] = useState<MiniMockDomainOption[]>([]);

  // Load baseline domains and initial coverage on open
  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    async function loadInitial() {
      setIsLoadingCoverage(true);
      setErrorMsg(null);
      try {
        const data = await fetchMiniMockCoverage(undefined, undefined, 10);
        if (isMounted) {
          setCoverageData(data);
          if (data.available_domains) {
            setAvailableDomains(data.available_domains);
          }
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : "Failed to load syllabus scope data.";
          setErrorMsg(msg);
        }
      } finally {
        if (isMounted) setIsLoadingCoverage(false);
      }
    }

    void loadInitial();
    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  // Selected topic IDs array for API
  const activeTopicIds = useMemo(() => {
    return Array.from(selectedConceptIds);
  }, [selectedConceptIds]);

  const activeSubjectIds = useMemo(() => {
    return Array.from(selectedDomainIds);
  }, [selectedDomainIds]);

  // Refresh coverage whenever scope or requested question count changes
  const refreshCoverage = useCallback(
    async (topics: string[], subjects: string[], count: number) => {
      setIsLoadingCoverage(true);
      setErrorMsg(null);
      try {
        const data = await fetchMiniMockCoverage(
          topics.length > 0 ? topics : undefined,
          subjects.length > 0 ? subjects : undefined,
          count
        );
        setCoverageData(data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to calculate question coverage.";
        setErrorMsg(msg);
      } finally {
        setIsLoadingCoverage(false);
      }
    },
    []
  );

  const handleToggleDomain = (domainId: string) => {
    const nextDomains = new Set(selectedDomainIds);
    const nextConcepts = new Set(selectedConceptIds);

    const domain = availableDomains.find((d) => d.domain_id === domainId);
    if (!domain) return;

    if (nextDomains.has(domainId)) {
      nextDomains.delete(domainId);
      // Deselect its concepts
      domain.concepts.forEach((c) => nextConcepts.delete(c.concept_id));
    } else {
      nextDomains.add(domainId);
      // Select all concepts in this domain
      domain.concepts.forEach((c) => nextConcepts.add(c.concept_id));
    }

    setSelectedDomainIds(nextDomains);
    setSelectedConceptIds(nextConcepts);
    void refreshCoverage(
      Array.from(nextConcepts),
      Array.from(nextDomains),
      questionCount
    );
  };

  const handleToggleConcept = (domainId: string, conceptId: string) => {
    const nextConcepts = new Set(selectedConceptIds);
    if (nextConcepts.has(conceptId)) {
      nextConcepts.delete(conceptId);
    } else {
      nextConcepts.add(conceptId);
    }
    setSelectedConceptIds(nextConcepts);

    // If all concepts of domain are selected, select domain; else deselect
    const domain = availableDomains.find((d) => d.domain_id === domainId);
    const nextDomains = new Set(selectedDomainIds);
    if (domain) {
      const allSelected = domain.concepts.every((c) => nextConcepts.has(c.concept_id));
      if (allSelected) {
        nextDomains.add(domainId);
      } else {
        nextDomains.delete(domainId);
      }
    }
    setSelectedDomainIds(nextDomains);

    void refreshCoverage(
      Array.from(nextConcepts),
      Array.from(nextDomains),
      questionCount
    );
  };

  const handleSelectAll = () => {
    const allDomains = new Set(availableDomains.map((d) => d.domain_id));
    const allConcepts = new Set<string>();
    availableDomains.forEach((d) => d.concepts.forEach((c) => allConcepts.add(c.concept_id)));

    setSelectedDomainIds(allDomains);
    setSelectedConceptIds(allConcepts);
    void refreshCoverage(Array.from(allConcepts), Array.from(allDomains), questionCount);
  };

  const handleClearAll = () => {
    setSelectedDomainIds(new Set());
    setSelectedConceptIds(new Set());
    void refreshCoverage([], [], questionCount);
  };

  const handleSizeChange = (newCount: number) => {
    setQuestionCount(newCount);
    void refreshCoverage(activeTopicIds, activeSubjectIds, newCount);
  };

  const handleCreateMock = async () => {
    if (!coverageData || coverageData.eligible_count === 0) return;
    setIsGenerating(true);
    setErrorMsg(null);

    const title =
      customTitle.trim() ||
      `Personalized Mini Mock (${questionCount} Qs • ${
        selectedConceptIds.size > 0 ? `${selectedConceptIds.size} Topics` : "All Pharmacology"
      })`;

    try {
      await onGenerateMock({
        blueprintName: "mini_mock",
        userId: studentId,
        customTitle: title,
        questionCount,
        durationMinutes: coverageData.estimated_duration_minutes,
        topicIds: activeTopicIds.length > 0 ? activeTopicIds : undefined,
        subjectIds: activeSubjectIds.length > 0 ? activeSubjectIds : undefined,
      });
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create mini mock session.";
      setErrorMsg(msg);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!isOpen) return null;

  const totalSelectedTopicsCount = selectedConceptIds.size;
  const eligiblePool = coverageData?.eligible_count ?? 0;
  const achievableCount = coverageData?.achievable_count ?? 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-sm animate-enter">
      <div className="w-full max-w-3xl max-h-[92vh] flex flex-col rounded-2xl bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)] shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-[rgba(96,165,250,0.15)] flex items-center justify-center text-[var(--color-accent)]">
              <SlidersHorizontal size={18} weight="bold" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-[var(--color-text-primary)]">
                Personalized Mini Mock Builder
              </h2>
              <p className="text-[11px] text-[var(--color-text-secondary)] font-mono">
                Real Eligible Questions • Transparent Blueprint • No Fake Scaling
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-raised)] transition-colors"
            aria-label="Close modal"
          >
            <X size={18} weight="bold" />
          </button>
        </div>

        {/* Wizard Step Progress Bar */}
        <div className="px-5 py-2.5 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-base)] flex items-center justify-between text-xs font-mono">
          <button
            type="button"
            onClick={() => setStep(1)}
            className={`flex items-center gap-1.5 transition-colors ${
              step === 1 ? "text-[var(--color-accent)] font-bold" : "text-[var(--color-text-tertiary)]"
            }`}
          >
            <span className="h-5 w-5 rounded-full border border-current flex items-center justify-center text-[10px]">
              1
            </span>
            <span>Select Scope</span>
          </button>

          <span className="text-[var(--color-border-subtle)]">&rarr;</span>

          <button
            type="button"
            onClick={() => setStep(2)}
            className={`flex items-center gap-1.5 transition-colors ${
              step === 2 ? "text-[var(--color-accent)] font-bold" : "text-[var(--color-text-tertiary)]"
            }`}
          >
            <span className="h-5 w-5 rounded-full border border-current flex items-center justify-center text-[10px]">
              2
            </span>
            <span>Paper Size</span>
          </button>

          <span className="text-[var(--color-border-subtle)]">&rarr;</span>

          <button
            type="button"
            onClick={() => setStep(3)}
            className={`flex items-center gap-1.5 transition-colors ${
              step === 3 ? "text-[var(--color-accent)] font-bold" : "text-[var(--color-text-tertiary)]"
            }`}
          >
            <span className="h-5 w-5 rounded-full border border-current flex items-center justify-center text-[10px]">
              3
            </span>
            <span>Review &amp; Generate</span>
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {errorMsg && (
            <div className="p-3 rounded-lg bg-[rgb(252_165_165/0.1)] border border-[var(--color-status-error)]/30 text-xs text-[var(--color-status-error)] flex items-center gap-2">
              <WarningCircle size={16} weight="bold" className="shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* ========================================================================= */}
          {/* STEP 1: SELECT SYLLABUS TOPICS / UNITS                                    */}
          {/* ========================================================================= */}
          {step === 1 && (
            <div className="space-y-4 animate-enter">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="text-xs font-semibold uppercase font-mono text-[var(--color-text-secondary)]">
                    Choose Subjects &amp; Concepts to Test
                  </h3>
                  <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">
                    Select units or individual concepts. Questions will be allocated across chosen topics.
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleSelectAll}
                    className="text-xs h-7 text-[var(--color-accent)]"
                  >
                    Select All
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleClearAll}
                    className="text-xs h-7 text-[var(--color-text-tertiary)]"
                  >
                    Clear
                  </Button>
                </div>
              </div>

              {/* Domains and Concepts Accordion Grid */}
              <div className="space-y-3 max-h-[48vh] overflow-y-auto pr-1">
                {availableDomains.map((dom) => {
                  const isDomainSelected = selectedDomainIds.has(dom.domain_id);
                  const selectedInDomain = dom.concepts.filter((c) =>
                    selectedConceptIds.has(c.concept_id)
                  ).length;

                  return (
                    <div
                      key={dom.domain_id}
                      className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/50 overflow-hidden"
                    >
                      {/* Domain Header Row */}
                      <div className="flex items-center justify-between p-3 bg-[var(--color-surface-raised)]/80">
                        <label className="flex items-center gap-2.5 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            checked={isDomainSelected || selectedInDomain === dom.concepts.length}
                            onChange={() => handleToggleDomain(dom.domain_id)}
                            className="rounded h-4 w-4 text-[var(--color-accent)] focus:ring-[var(--color-accent)] cursor-pointer"
                          />
                          <span className="text-xs font-bold text-[var(--color-text-primary)]">
                            {dom.display_name}
                          </span>
                        </label>

                        <div className="flex items-center gap-2 font-mono text-[10px]">
                          <Badge variant="default">
                            {dom.total_questions} verified Qs
                          </Badge>
                          <span className="text-[var(--color-text-tertiary)]">
                            ({selectedInDomain}/{dom.concepts.length} concepts)
                          </span>
                        </div>
                      </div>

                      {/* Concepts List inside Domain */}
                      <div className="p-3 grid grid-cols-1 sm:grid-cols-2 gap-2 border-t border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
                        {dom.concepts.map((concept) => {
                          const isConceptSelected = selectedConceptIds.has(concept.concept_id);
                          return (
                            <label
                              key={concept.concept_id}
                              className={`flex items-start justify-between gap-2 p-2 rounded-lg border text-xs cursor-pointer transition-colors ${
                                isConceptSelected
                                  ? "border-[var(--color-accent)] bg-[rgb(96_165_250/0.08)] text-[var(--color-text-primary)] font-medium"
                                  : "border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/30 text-[var(--color-text-secondary)] hover:border-[var(--color-border-focus)]"
                              }`}
                            >
                              <div className="flex items-start gap-2 flex-1">
                                <input
                                  type="checkbox"
                                  checked={isConceptSelected}
                                  onChange={() => handleToggleConcept(dom.domain_id, concept.concept_id)}
                                  className="mt-0.5 rounded h-3.5 w-3.5 text-[var(--color-accent)] focus:ring-[var(--color-accent)] cursor-pointer"
                                />
                                <span className="text-[11px] leading-tight line-clamp-2">
                                  {concept.name}
                                </span>
                              </div>
                              <span className="font-mono text-[10px] text-[var(--color-text-tertiary)] shrink-0">
                                {concept.question_count} Qs
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Scope Summary Footer */}
              <div className="p-3 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] flex items-center justify-between text-xs font-mono">
                <span className="text-[var(--color-text-secondary)]">
                  Selected: <strong>{totalSelectedTopicsCount}</strong> topics across{" "}
                  <strong>{selectedDomainIds.size}</strong> subjects
                </span>
                <span className="text-[var(--color-accent)] font-semibold">
                  Eligible Verified Pool: {eligiblePool} Qs
                </span>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* STEP 2: CHOOSE PAPER SIZE & TEST CONFIGURATION                            */}
          {/* ========================================================================= */}
          {step === 2 && (
            <div className="space-y-4 animate-enter">
              <div>
                <h3 className="text-xs font-semibold uppercase font-mono text-[var(--color-text-secondary)]">
                  Select Paper Size &amp; Duration
                </h3>
                <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">
                  Questions are distributed evenly across your selected topics up to the verified pool.
                </p>
              </div>

              {/* Preset Paper Size Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {PAPER_SIZES.map((size) => {
                  const isSelected = questionCount === size.count;
                  const isAvailable = eligiblePool >= size.count;

                  return (
                    <Card
                      key={size.count}
                      onClick={() => handleSizeChange(size.count)}
                      className={`cursor-pointer transition-all border p-4 ${
                        isSelected
                          ? "border-[var(--color-accent)] ring-1 ring-[var(--color-accent)]/40 bg-[var(--color-surface-raised)]"
                          : "border-[var(--color-border-subtle)] hover:border-[var(--color-border-focus)] bg-[var(--color-surface-base)]"
                      } ${!isAvailable ? "opacity-70" : ""}`}
                    >
                      <div className="flex items-center justify-between">
                        <Badge variant={isSelected ? "primary" : "default"} className="font-mono text-[10px]">
                          {size.tag}
                        </Badge>
                        {isSelected && <Check size={16} weight="bold" className="text-[var(--color-accent)]" />}
                      </div>

                      <div className="mt-3 text-lg font-bold text-[var(--color-text-primary)]">
                        {size.label}
                      </div>

                      <div className="mt-1 flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-secondary)]">
                        <Clock size={13} weight="bold" />
                        <span>~{size.durationMin} mins (1.8m/Q)</span>
                      </div>

                      {!isAvailable && (
                        <div className="mt-2 text-[10px] text-[var(--color-status-warning)] font-mono">
                          Pool shortfall: only {eligiblePool} available
                        </div>
                      )}
                    </Card>
                  );
                })}
              </div>

              {/* Custom Title Input */}
              <div className="space-y-1.5 pt-2">
                <label className="text-xs font-medium text-[var(--color-text-secondary)] font-mono">
                  Custom Paper Title (Optional):
                </label>
                <input
                  type="text"
                  placeholder="e.g., Autonomic & CVS Mini Mock 01"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-[var(--color-text-primary)] focus:border-[var(--color-accent)] outline-none"
                />
              </div>

              {/* Marking Scheme Reminder */}
              <div className="p-3.5 rounded-xl bg-[rgba(96,165,250,0.06)] border border-[var(--color-accent)]/20 space-y-1 text-xs">
                <div className="font-semibold text-[var(--color-accent)] flex items-center gap-1.5 font-mono">
                  <ShieldCheck size={15} weight="bold" />
                  Official NBEMS Marking Rule
                </div>
                <p className="text-[var(--color-text-secondary)] text-[11px] leading-relaxed">
                  Every correct response awards <strong>+4 marks</strong>. Every incorrect attempt incurs a deduction of{" "}
                  <strong>-1 mark</strong>. Unattempted questions incur <strong>0 marks</strong>.
                </p>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* STEP 3: BLUEPRINT TRANSPARENCY & ALLOCATION AUDIT                         */}
          {/* ========================================================================= */}
          {step === 3 && (
            <div className="space-y-4 animate-enter">
              <div>
                <h3 className="text-xs font-semibold uppercase font-mono text-[var(--color-text-secondary)]">
                  Review Paper Blueprint &amp; Topic Allocation
                </h3>
                <p className="text-xs text-[var(--color-text-tertiary)] mt-0.5">
                  Inspect the question distribution before generation. We never fabricate questions or scale estimates.
                </p>
              </div>

              {/* Coverage Gaps / Shortfall Warning */}
              {coverageData?.coverage_gaps && coverageData.coverage_gaps.length > 0 && (
                <div className="p-3.5 rounded-xl bg-[rgb(252_211_77/0.1)] border border-[var(--color-status-warning)]/30 text-xs text-[var(--color-status-warning)] space-y-1">
                  <div className="font-semibold flex items-center gap-1.5">
                    <WarningCircle size={15} weight="bold" />
                    Coverage Notice
                  </div>
                  {coverageData.coverage_gaps.map((gap, gIdx) => (
                    <p key={gIdx} className="text-[11px] leading-relaxed">
                      {gap}
                    </p>
                  ))}
                </div>
              )}

              {/* Blueprint Summary Card */}
              <Card className="border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/60 p-4 space-y-3">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-2.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                    <span className="text-[var(--color-text-tertiary)] block text-[10px]">Paper Size</span>
                    <strong className="text-sm text-[var(--color-text-primary)]">
                      {achievableCount} / {questionCount} Qs
                    </strong>
                  </div>

                  <div className="p-2.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                    <span className="text-[var(--color-text-tertiary)] block text-[10px]">Estimated Time</span>
                    <strong className="text-sm text-[var(--color-accent)]">
                      {coverageData?.estimated_duration_minutes ?? 18} mins
                    </strong>
                  </div>

                  <div className="p-2.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                    <span className="text-[var(--color-text-tertiary)] block text-[10px]">Marking</span>
                    <strong className="text-sm text-emerald-400">+4 / -1</strong>
                  </div>

                  <div className="p-2.5 rounded bg-[var(--color-surface-base)] border border-[var(--color-border-subtle)]">
                    <span className="text-[var(--color-text-tertiary)] block text-[10px]">Max Score</span>
                    <strong className="text-sm text-[var(--color-text-primary)]">
                      {achievableCount * 4} marks
                    </strong>
                  </div>
                </div>

                {/* Per-Topic Question Distribution Table */}
                <div className="pt-2">
                  <div className="text-[11px] font-semibold text-[var(--color-text-secondary)] font-mono uppercase pb-1.5 flex items-center justify-between">
                    <span>Allocated Concepts ({coverageData?.concepts_breakdown.length || 0})</span>
                    <span>Available In Pool</span>
                  </div>

                  <div className="max-h-40 overflow-y-auto divide-y divide-[var(--color-border-subtle)] rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-surface-base)]">
                    {coverageData?.concepts_breakdown && coverageData.concepts_breakdown.length > 0 ? (
                      coverageData.concepts_breakdown.map((item) => (
                        <div
                          key={item.concept_id}
                          className="p-2.5 flex items-center justify-between text-xs font-mono"
                        >
                          <span className="text-[var(--color-text-primary)] line-clamp-1 flex-1 font-sans">
                            {item.concept_name}
                          </span>
                          <span className="text-[var(--color-accent)] font-bold ml-2">
                            {item.eligible_count} Qs
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="p-4 text-center text-xs text-[var(--color-text-tertiary)]">
                        No concepts currently selected. Defaulting to all verified pharmacology topics.
                      </div>
                    )}
                  </div>
                </div>
              </Card>

              {/* Prediction Disclaimer */}
              <div className="p-3 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)] text-[11px] text-[var(--color-text-tertiary)] leading-relaxed italic">
                * Note: Mini mocks measure accuracy and time efficiency on selected topics. They do not simulate full-length NBEMS standard distribution and must not be interpreted as an official GPAT predicted score.
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Controls */}
        <div className="flex items-center justify-between px-5 py-3.5 border-t border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]/40">
          <div>
            {step > 1 ? (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => setStep((s) => (s - 1) as 1 | 2)}
                disabled={isGenerating}
                className="gap-1.5 text-xs font-mono"
              >
                <ArrowLeft size={14} weight="bold" />
                Previous
              </Button>
            ) : (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-xs text-[var(--color-text-tertiary)]"
              >
                Cancel
              </Button>
            )}
          </div>

          <div>
            {step < 3 ? (
              <Button
                type="button"
                variant="primary"
                size="sm"
                onClick={() => setStep((s) => (s + 1) as 2 | 3)}
                disabled={isLoadingCoverage || eligiblePool === 0}
                className="gap-1.5 text-xs font-mono font-semibold px-4"
              >
                <span>Continue</span>
                <ArrowRight size={14} weight="bold" />
              </Button>
            ) : (
              <Button
                type="button"
                variant="primary"
                size="sm"
                onClick={handleCreateMock}
                disabled={isGenerating || achievableCount === 0}
                className="gap-2 text-xs font-mono font-bold px-5 bg-[var(--color-accent)] hover:opacity-90"
              >
                <Sparkle size={15} weight="bold" />
                <span>{isGenerating ? "Allocating Mock..." : "Generate & Launch Mock"}</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
