import {
  Pill,
  Flask,
  Atom,
  Plant,
  Dna
} from "@phosphor-icons/react";

export type ExamSubjectId =
  | "pharmacology"
  | "pharmaceutics"
  | "pharmaceutical_chemistry"
  | "pharmacognosy"
  | "other_subjects";

export interface SubjectTheme {
  id: ExamSubjectId;
  name: string;
  shortName: string;
  colorName: string;
  badgeBg: string;
  badgeBorder: string;
  badgeText: string;
  borderHover: string;
  accentText: string;
  glowColor: string;
  icon: React.ComponentType<{ size?: number; weight?: "bold" | "regular"; className?: string; style?: React.CSSProperties }>;
}

export const SUBJECT_THEMES: Record<ExamSubjectId, SubjectTheme> = {
  pharmacology: {
    id: "pharmacology",
    name: "Pharmacology & Allied Subjects",
    shortName: "Pharmacology",
    colorName: "Forest Green",
    badgeBg: "rgba(74, 222, 128, 0.08)",
    badgeBorder: "rgba(74, 222, 128, 0.25)",
    badgeText: "#86EFAC",
    borderHover: "rgba(74, 222, 128, 0.45)",
    accentText: "#4ADE80",
    glowColor: "rgba(74, 222, 128, 0.15)",
    icon: Pill,
  },
  pharmaceutics: {
    id: "pharmaceutics",
    name: "Pharmaceutics & Allied Subjects",
    shortName: "Pharmaceutics",
    colorName: "Sky Blue",
    badgeBg: "rgba(96, 165, 250, 0.08)",
    badgeBorder: "rgba(96, 165, 250, 0.25)",
    badgeText: "#93C5FD",
    borderHover: "rgba(96, 165, 250, 0.45)",
    accentText: "#60A5FA",
    glowColor: "rgba(96, 165, 250, 0.15)",
    icon: Flask,
  },
  pharmaceutical_chemistry: {
    id: "pharmaceutical_chemistry",
    name: "Pharmaceutical Chemistry & Allied Subjects",
    shortName: "Pharm Chemistry",
    colorName: "Warm Amber",
    badgeBg: "rgba(251, 191, 36, 0.08)",
    badgeBorder: "rgba(251, 191, 36, 0.25)",
    badgeText: "#FDE047",
    borderHover: "rgba(251, 191, 36, 0.45)",
    accentText: "#FBBF24",
    glowColor: "rgba(251, 191, 36, 0.15)",
    icon: Atom,
  },
  pharmacognosy: {
    id: "pharmacognosy",
    name: "Pharmacognosy & Allied Subjects",
    shortName: "Pharmacognosy",
    colorName: "Muted Violet",
    badgeBg: "rgba(192, 132, 252, 0.08)",
    badgeBorder: "rgba(192, 132, 252, 0.25)",
    badgeText: "#D8B4FE",
    borderHover: "rgba(192, 132, 252, 0.45)",
    accentText: "#C084FC",
    glowColor: "rgba(192, 132, 252, 0.15)",
    icon: Plant,
  },
  other_subjects: {
    id: "other_subjects",
    name: "Other B.Pharm Subjects (Biotechnology, Jurisprudence)",
    shortName: "Other Subjects",
    colorName: "Teal Cyan",
    badgeBg: "rgba(45, 212, 191, 0.08)",
    badgeBorder: "rgba(45, 212, 191, 0.25)",
    badgeText: "#5EEAD4",
    borderHover: "rgba(45, 212, 191, 0.45)",
    accentText: "#2DD4BF",
    glowColor: "rgba(45, 212, 191, 0.15)",
    icon: Dna,
  },
};

export function getSubjectTheme(subjectId?: string): SubjectTheme {
  if (!subjectId) {
    return SUBJECT_THEMES.pharmacology;
  }
  const normalized = subjectId.toLowerCase().trim();
  if (normalized.includes("pharmacology") || normalized.includes("ans") || normalized.includes("cns") || normalized.includes("cvs")) {
    return SUBJECT_THEMES.pharmacology;
  }
  if (normalized.includes("pharmaceutics") || normalized.includes("dispensing") || normalized.includes("biopharmaceutics")) {
    return SUBJECT_THEMES.pharmaceutics;
  }
  if (normalized.includes("chemistry") || normalized.includes("analysis") || normalized.includes("biochemistry")) {
    return SUBJECT_THEMES.pharmaceutical_chemistry;
  }
  if (normalized.includes("pharmacognosy") || normalized.includes("phytochemistry") || normalized.includes("plant")) {
    return SUBJECT_THEMES.pharmacognosy;
  }
  if (normalized.includes("other") || normalized.includes("biotechnology") || normalized.includes("jurisprudence") || normalized.includes("microbiology")) {
    return SUBJECT_THEMES.other_subjects;
  }
  return SUBJECT_THEMES.pharmacology;
}
