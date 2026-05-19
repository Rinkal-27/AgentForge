import type { AgentCard } from "../api";

interface Props {
  agents: AgentCard[];
  selected: string | null;
  onSelect: (name: string) => void;
}

const ROLE_EMOJI: Record<string, string> = {
  coder: "💻",
  analyst: "📊",
  designer: "🎨",
  reviewer: "🔍",
};

export default function AgentCardList({ agents, selected, onSelect }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {agents.map((a) => {
        const isSelected = selected === a.name;
        return (
          <button
            key={a.name}
            onClick={() => onSelect(a.name)}
            className={`text-left rounded-xl p-4 border transition-all ${
              isSelected
                ? "border-indigo-400 bg-indigo-500/10 ring-2 ring-indigo-400/40"
                : "border-slate-800 bg-slate-900/60 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl">{ROLE_EMOJI[a.name] ?? "🤖"}</span>
              <h3 className="font-semibold text-slate-100">{a.display_name}</h3>
            </div>
            <p className="text-xs text-slate-400 mb-2 leading-snug">
              {a.description}
            </p>
            <div className="flex flex-wrap gap-1 mb-2">
              {a.skills.map((s) => (
                <span
                  key={s.name}
                  title={s.description}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300"
                >
                  {s.name}
                </span>
              ))}
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-500">
              <span className="font-mono truncate">{a.model}</span>
              <span>
                {a.avg_latency_ms != null
                  ? `${Math.round(a.avg_latency_ms)} ms · ${a.invocations} calls`
                  : "no calls yet"}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
