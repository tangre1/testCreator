import { useEffect, useState } from "react";
import { InlineMath } from "react-katex";

import {
  getBanks,
  getTopics,
  generateExam,
  generatePreview,
} from "./api";

import "./App.css";

type TopicWeights = Record<string, number>;
type InputValues = Record<string, string>;

type PreviewQuestion = {
  id: string;
  topic: string;
  latex: string;
};

function App() {
  const [banks, setBanks] = useState<string[]>([]);
  const [selectedBank, setSelectedBank] = useState("");

  const [topics, setTopics] = useState<string[]>([]);
  const [weights, setWeights] = useState<TopicWeights>({});
  const [inputValues, setInputValues] = useState<InputValues>({});

  const [totalQuestions, setTotalQuestions] = useState(8);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [previewQuestions, setPreviewQuestions] = useState<PreviewQuestion[]>([]);
  const [seed, setSeed] = useState<number | null>(null);
  const [latexCode, setLatexCode] = useState("");

  /* -------------------------
     Load banks
  ------------------------- */
  useEffect(() => {
    getBanks()
      .then(setBanks)
      .catch(() => setError("Failed to load question banks"));
  }, []);

  /* -------------------------
     Load topics
  ------------------------- */
  useEffect(() => {
    if (!selectedBank) return;

    getTopics(selectedBank)
      .then((topics) => {
        setTopics(topics);

        const initialWeight = 1 / topics.length;
        const w: TopicWeights = {};
        const i: InputValues = {};

        topics.forEach((t) => {
          w[t] = initialWeight;
          i[t] = (initialWeight * 100).toFixed(1);
        });

        setWeights(w);
        setInputValues(i);
        setPreviewQuestions([]);
        setLatexCode("");
        setSeed(null);
      })
      .catch(() => setError("Failed to load topics"));
  }, [selectedBank]);

  /* -------------------------
     Redistribute weights
  ------------------------- */
  function redistribute(topic: string, percent: number) {
    const remaining = Math.max(0, 100 - percent);
    const others = topics.filter((t) => t !== topic);

    if (others.length === 0) return;

    const currentSum = others.reduce(
      (sum, t) => sum + (weights[t] ?? 0),
      0
    );

    const newWeights: TopicWeights = {};
    newWeights[topic] = percent / 100;

    others.forEach((t) => {
      const proportion =
        currentSum === 0 ? 1 / others.length : weights[t] / currentSum;
      newWeights[t] = (remaining * proportion) / 100;
    });

    setWeights(newWeights);

    const newInputs: InputValues = {};
    topics.forEach((t) => {
      newInputs[t] = (newWeights[t] * 100).toFixed(1);
    });
    setInputValues(newInputs);
  }

  /* -------------------------
     Input handlers
  ------------------------- */
  function handleInputChange(topic: string, value: string) {
    setInputValues((prev) => ({ ...prev, [topic]: value }));
  }

  function handleInputBlur(topic: string) {
    const num = Number(inputValues[topic]);
    if (isNaN(num)) return;
    redistribute(topic, Math.min(100, Math.max(0, num)));
  }

  function handleSliderChange(topic: string, value: number) {
    redistribute(topic, value * 100);
  }

  /* -------------------------
     Generate preview
  ------------------------- */
  async function handleGeneratePreview() {
    setLoading(true);
    setError(null);

    try {
      const newSeed = Date.now();
      setSeed(newSeed);

      const preview = await generatePreview(
        selectedBank,
        totalQuestions,
        weights,
        newSeed
      );

      setPreviewQuestions(preview.questions);
      setLatexCode("");
    } catch (err: any) {
      setError(err.message || "Failed to generate preview");
    } finally {
      setLoading(false);
    }
  }

  /* -------------------------
     Generate LaTeX
  ------------------------- */
  async function handleGenerateLatex() {
    if (seed === null) return;

    try {
      const latex = await generateExam(
        selectedBank,
        totalQuestions,
        weights,
        seed
      );
      setLatexCode(latex);
    } catch (err: any) {
      setError(err.message || "Failed to generate LaTeX");
    }
  }

  function copyLatex() {
    navigator.clipboard.writeText(latexCode);
  }

  /* -------------------------
     Render
  ------------------------- */
  return (
    <div className="app">
      <h1>CSU Exam Generator</h1>

      {error && <p className="error">{error}</p>}

      <div className="layout">
        {/* LEFT PANEL — CONTROLS */}
        <div className="left-panel">
          <label>Question Bank</label>
          <select
            value={selectedBank}
            onChange={(e) => setSelectedBank(e.target.value)}
          >
            <option value="">-- Select a bank --</option>
            {banks.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>

          <label style={{ marginTop: "1rem" }}>Total Questions</label>
          <input
            type="number"
            min={1}
            value={totalQuestions}
            onChange={(e) => setTotalQuestions(Number(e.target.value))}
          />

          {topics.length > 0 && (
            <div style={{ marginTop: "1.5rem" }}>
              <h3>Topic Distribution</h3>

              {topics.map((topic) => (
                <div key={topic} className="topic-row">
                  <div className="topic-header">
                    <strong>{topic}</strong>

                    <input
                      type="text"
                      value={inputValues[topic]}
                      onChange={(e) =>
                        handleInputChange(topic, e.target.value)
                      }
                      onBlur={() => handleInputBlur(topic)}
                    />
                    %
                  </div>

                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.01}
                    value={weights[topic] ?? 0}
                    onChange={(e) =>
                      handleSliderChange(topic, Number(e.target.value))
                    }
                  />
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleGeneratePreview}
            disabled={loading || !selectedBank}
            style={{ marginTop: "1.5rem" }}
          >
            {loading ? "Generating..." : "Generate Preview"}
          </button>
        </div>

        {/* RIGHT PANEL — OUTPUT */}
        <div className="right-panel">
          {previewQuestions.length > 0 && (
            <div>
              <h2>Question Preview</h2>

              {previewQuestions.map((q, idx) => (
                <div key={q.id} className="question-card">
                  <div className="question-meta">
                    <strong>Question {idx + 1}</strong>
                    <span className="topic-pill">{q.topic}</span>
                  </div>
                  
                  <div style={{ whiteSpace: "pre-wrap" }}>
                    {q.latex}
                  </div>

                </div>
              ))}

              <button
                className="secondary"
                style={{ marginTop: "1rem" }}
                onClick={handleGenerateLatex}
              >
                Show LaTeX Code
              </button>
            </div>
          )}

          {latexCode && (
            <div>
              <h2>LaTeX Output</h2>

              <textarea value={latexCode} readOnly />

              <button onClick={copyLatex} style={{ marginTop: "0.75rem" }}>
                Copy to Clipboard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
