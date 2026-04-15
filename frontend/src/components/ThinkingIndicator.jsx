import { useState, useEffect, useRef } from 'react';
import { Brain, Search, FileSearch, Sparkles, PenTool, CheckCircle } from 'lucide-react';

const THINKING_STAGES = [
  { icon: Search,     label: '正在向量化查询...',         minSec: 0  },
  { icon: FileSearch,  label: '检索知识库文档...',         minSec: 3  },
  { icon: Brain,       label: '分析参考文档...',           minSec: 8  },
  { icon: Sparkles,    label: 'DeepSeek 深度推理中...',    minSec: 20 },
  { icon: PenTool,     label: '组织回答内容...',           minSec: 50 },
  { icon: CheckCircle, label: '即将完成，请稍候...',       minSec: 80 },
];

const STAGE_UPDATE_INTERVAL = 10_000;
const PERCENT_TICK_INTERVAL = 1_000;

function calcProgress(elapsedSec) {
  if (elapsedSec <= 0) return 1;
  if (elapsedSec < 10) return Math.min(Math.round(elapsedSec * 3), 28);
  if (elapsedSec < 30) return 28 + Math.round((elapsedSec - 10) * 1.5);
  if (elapsedSec < 60) return 58 + Math.round((elapsedSec - 30) * 0.7);
  if (elapsedSec < 90) return 79 + Math.round((elapsedSec - 60) * 0.4);
  return Math.min(92 + Math.round((elapsedSec - 90) * 0.08), 99);
}

function getStage(elapsedSec) {
  let stage = THINKING_STAGES[0];
  for (const s of THINKING_STAGES) {
    if (elapsedSec >= s.minSec) stage = s;
  }
  return stage;
}

export default function ThinkingIndicator({ startTime }) {
  const [elapsedSec, setElapsedSec] = useState(0);
  const [stage, setStage] = useState(THINKING_STAGES[0]);
  const [flash, setFlash] = useState(false);
  const tickRef = useRef(null);
  const stageRef = useRef(null);

  useEffect(() => {
    const t0 = startTime || Date.now();

    const tick = () => {
      const sec = Math.floor((Date.now() - t0) / 1000);
      setElapsedSec(sec);
      setFlash(prev => !prev);
    };
    tick();
    tickRef.current = setInterval(tick, PERCENT_TICK_INTERVAL);

    const updateStage = () => {
      const sec = Math.floor((Date.now() - t0) / 1000);
      setStage(getStage(sec));
    };
    updateStage();
    stageRef.current = setInterval(updateStage, STAGE_UPDATE_INTERVAL);

    return () => {
      clearInterval(tickRef.current);
      clearInterval(stageRef.current);
    };
  }, [startTime]);

  const percent = calcProgress(elapsedSec);
  const StageIcon = stage.icon;

  return (
    <div className="thinking-indicator flex flex-col gap-2 py-1 min-w-[220px]">
      <div className="flex items-center gap-2">
        <StageIcon size={15} className="thinking-icon text-[var(--color-accent)]" />
        <span className="text-sm text-[var(--color-text-secondary)] thinking-stage-text">
          {stage.label}
        </span>
      </div>

      <div className="flex items-center gap-2.5">
        <div className="flex-1 h-1.5 rounded-full bg-[var(--color-dark-500)] overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[var(--color-accent-dim)] to-[var(--color-accent)] transition-all duration-700 ease-out"
            style={{ width: `${percent}%` }}
          />
        </div>
        <span className={`text-xs font-mono min-w-[3ch] text-right tabular-nums transition-opacity duration-300 ${
          flash ? 'opacity-100 text-[var(--color-accent)]' : 'opacity-40 text-[var(--color-text-muted)]'
        }`}>
          {percent}%
        </span>
      </div>

      <span className="text-[10px] text-[var(--color-text-muted)]">
        已用时 {elapsedSec}s
      </span>
    </div>
  );
}
