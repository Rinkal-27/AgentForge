import type { RouteResult } from "../api";
import MarkdownOutput from "./MarkdownOutput";

interface Props {
  result: RouteResult;
}

const ROLE_EMOJI: Record<string, string> = {
  coder: "💻",
  analyst: "📊",
  designer: "🎨",
  reviewer: "🔍",
};

export default function RouteResultView({ result }: Props) {
  return (
    <div className="space-y-4">
      <section>
        <h3 className="text-xs uppercase tracking-wider text-slate-400 mb-2">
          Plan ({result.plan.length} step{result.plan.length === 1 ? "" : "s"})
        </h3>
        <ol className="flex flex-wrap items-center gap-2 text-sm">
          {result.plan.map((step, i) => (
            <li key={i} className="flex items-center gap-2">
              <span className="px-2 py-1 rounded-lg bg-slate-800 border border-slate-700">
                <span className="mr-1">{ROLE_EMOJI[step.agent] ?? "🤖"}</span>
                <span className="font-medium">{step.agent}</span>
              </span>
              {i < result.plan.length - 1 && (
                <span className="text-slate-600">→</span>
              )}
            </li>
          ))}
        </ol>
      </section>

      <section>
        <h3 className="text-xs uppercase tracking-wider text-slate-400 mb-2">
          Final output
        </h3>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <MarkdownOutput text={result.final} />
        </div>
      </section>

      <details className="rounded-xl border border-slate-800 bg-slate-900/60">
        <summary className="cursor-pointer select-none px-4 py-2 text-sm text-slate-300">
          Execution trace ({result.trace.length})
        </summary>
        <div className="px-4 pb-4 space-y-3">
          {result.trace.map((step) => (
            <div
              key={step.step}
              className="rounded-lg border border-slate-800 bg-slate-950/50 p-3"
            >
              <div className="text-xs text-slate-400 mb-1">
                Step {step.step} ·{" "}
                <span className="font-medium text-slate-200">
                  {ROLE_EMOJI[step.agent] ?? "🤖"} {step.agent}
                </span>
                {step.uses.length > 0 && (
                  <span className="ml-2 text-slate-500">
                    uses: [{step.uses.join(", ")}]
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mb-2 italic">
                {step.task}
              </p>
              <pre className="text-[11px] text-slate-300 whitespace-pre-wrap break-words">
                {step.output_preview}
                {step.output_preview.length >= 400 && "…"}
              </pre>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}
