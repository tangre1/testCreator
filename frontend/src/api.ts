// frontend/src/api.ts

const API_BASE = "http://127.0.0.1:8000";

/* =========================
   Types
========================= */

export type PreviewQuestion = {
  id: string;
  topic: string;
  latex: string;
};

export type PreviewResponse = {
  course: string;
  unit: string;
  questions: PreviewQuestion[];
};

/* =========================
   Banks / Topics
========================= */

/**
 * Fetch list of available question banks
 */
export async function getBanks(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/banks`);

  if (!res.ok) {
    throw new Error("Failed to fetch question banks");
  }

  return res.json();
}

/**
 * Fetch topics for a given question bank
 */
export async function getTopics(bankFile: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/banks/${bankFile}/topics`);

  if (!res.ok) {
    throw new Error("Failed to fetch topics");
  }

  return res.json();
}

/* =========================
   Preview (STRUCTURED)
========================= */

/**
 * Generate a preview of the selected question set (NO LaTeX assembly)
 */
export async function generatePreview(
  bankFile: string,
  totalQuestions: number,
  topicWeights: Record<string, number>,
  seed: number
): Promise<PreviewResponse> {
  const res = await fetch(
    `${API_BASE}/generate-preview?bank_file=${encodeURIComponent(bankFile)}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        total_questions: totalQuestions,
        topic_weights: topicWeights,
        seed,
      }),
    }
  );

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText);
  }

  return res.json();
}

/* =========================
   Final Exam (LaTeX)
========================= */

/**
 * Generate the final LaTeX exam (must use SAME seed as preview)
 */
export async function generateExam(
  bankFile: string,
  totalQuestions: number,
  topicWeights: Record<string, number>,
  seed: number
): Promise<string> {
  const res = await fetch(
    `${API_BASE}/generate-exam?bank_file=${encodeURIComponent(bankFile)}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        total_questions: totalQuestions,
        topic_weights: topicWeights,
        seed,
      }),
    }
  );

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText);
  }

  return res.text();
}

/* =========================
   Download Utility
========================= */

/**
 * Trigger a browser download of the generated LaTeX
 */
export function downloadLatex(latex: string, filename = "exam.tex") {
  const blob = new Blob([latex], { type: "text/plain" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();

  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
