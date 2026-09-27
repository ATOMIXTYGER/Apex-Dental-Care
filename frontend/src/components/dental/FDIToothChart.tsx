import React from 'react';
import { ToothCondition, ToothConditionType } from '../../types';

interface FDIToothChartProps {
  teeth: Record<number, ToothCondition>;
  selectedTooth: number | null;
  onSelectTooth: (toothNumber: number) => void;
}

export const getConditionColor = (condition: ToothConditionType): string => {
  switch (condition) {
    case 'healthy':
      return '#10b981'; // Emerald
    case 'caries':
      return '#ef4444'; // Red
    case 'filled':
      return '#3b82f6'; // Blue
    case 'crown':
      return '#f59e0b'; // Amber
    case 'root_canal':
      return '#8b5cf6'; // Purple
    case 'missing':
      return '#94a3b8'; // Slate
    case 'extraction':
      return '#dc2626'; // Dark Red
    case 'fracture':
      return '#ea580c'; // Orange
    case 'sensitivity':
      return '#eab308'; // Yellow
    case 'mobility':
      return '#ec4899'; // Pink
    case 'bridge':
    case 'implant':
      return '#06b6d4'; // Cyan
    default:
      return '#64748b';
  }
};

export const getConditionBadgeClass = (condition: ToothConditionType): string => {
  switch (condition) {
    case 'healthy':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'caries':
      return 'bg-red-50 text-red-700 border-red-200';
    case 'filled':
      return 'bg-blue-50 text-blue-700 border-blue-200';
    case 'crown':
      return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'root_canal':
      return 'bg-purple-50 text-purple-700 border-purple-200';
    case 'missing':
      return 'bg-slate-100 text-slate-600 border-slate-300';
    case 'fracture':
      return 'bg-orange-50 text-orange-700 border-orange-200';
    default:
      return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

export const getToothName = (toothNumber: number): string => {
  const quad = Math.floor(toothNumber / 10);
  const pos = toothNumber % 10;

  const quadNames: Record<number, string> = {
    1: 'Upper Right',
    2: 'Upper Left',
    3: 'Lower Left',
    4: 'Lower Right',
  };

  const posNames: Record<number, string> = {
    1: 'Central Incisor',
    2: 'Lateral Incisor',
    3: 'Canine',
    4: 'First Premolar',
    5: 'Second Premolar',
    6: 'First Molar',
    7: 'Second Molar',
    8: 'Third Molar (Wisdom)',
  };

  return `${quadNames[quad] || ''} ${posNames[pos] || ''} (${toothNumber})`;
};

const ToothGraphic: React.FC<{
  toothNumber: number;
  conditionData?: ToothCondition;
  isSelected: boolean;
  onClick: () => void;
}> = ({ toothNumber, conditionData, isSelected, onClick }) => {
  const cond = conditionData?.current_condition || 'healthy';
  const color = getConditionColor(cond);
  const isMissing = cond === 'missing';

  return (
    <div
      onClick={onClick}
      className={`group flex flex-col items-center cursor-pointer p-1.5 rounded-xl transition-all duration-150 ${
        isSelected
          ? 'bg-teal-50 ring-2 ring-teal-500 scale-105 shadow-md'
          : 'hover:bg-slate-100 hover:scale-105'
      }`}
    >
      <span className="text-[11px] font-bold text-slate-700 mb-1 group-hover:text-teal-600">
        {toothNumber}
      </span>

      {/* Anatomical 5-surface Tooth Diagram */}
      <svg width="38" height="38" viewBox="0 0 40 40" className="drop-shadow-sm">
        {/* Outer Tooth Base */}
        <rect
          x="2"
          y="2"
          width="36"
          height="36"
          rx="6"
          fill={isMissing ? '#f1f5f9' : '#ffffff'}
          stroke={isSelected ? '#0d9488' : '#cbd5e1'}
          strokeWidth={isSelected ? '2' : '1.5'}
        />

        {!isMissing ? (
          <>
            {/* Buccal Surface (Top) */}
            <polygon points="4,4 36,4 28,12 12,12" fill={color} opacity="0.8" />
            {/* Lingual Surface (Bottom) */}
            <polygon points="4,36 36,36 28,28 12,28" fill={color} opacity="0.8" />
            {/* Mesial Surface (Left) */}
            <polygon points="4,4 12,12 12,28 4,36" fill={color} opacity="0.6" />
            {/* Distal Surface (Right) */}
            <polygon points="36,4 28,12 28,28 36,36" fill={color} opacity="0.6" />
            {/* Occlusal Center Surface */}
            <rect x="13" y="13" width="14" height="14" rx="2" fill={color} />
          </>
        ) : (
          /* Missing Tooth Cross */
          <g stroke="#94a3b8" strokeWidth="2">
            <line x1="8" y1="8" x2="32" y2="32" />
            <line x1="32" y1="8" x2="8" y2="32" />
          </g>
        )}
      </svg>

      <span
        className="mt-1 text-[9px] font-semibold uppercase px-1.5 py-0.5 rounded tracking-tighter truncate max-w-[46px]"
        style={{
          color: color,
          backgroundColor: `${color}18`,
        }}
      >
        {cond}
      </span>
    </div>
  );
};

export const FDIToothChart: React.FC<FDIToothChartProps> = ({
  teeth,
  selectedTooth,
  onSelectTooth,
}) => {
  // Quadrants
  const q1 = [18, 17, 16, 15, 14, 13, 12, 11]; // Upper Right
  const q2 = [21, 22, 23, 24, 25, 26, 27, 28]; // Upper Left
  const q4 = [48, 47, 46, 45, 44, 43, 42, 41]; // Lower Right
  const q3 = [31, 32, 33, 34, 35, 36, 37, 38]; // Lower Left

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 overflow-x-auto">
      {/* Chart Legend */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-800">FDI World Dental Federation Tooth Chart</h3>
          <p className="text-xs text-slate-500">
            Interactive 32 permanent teeth anatomical representation. Click any tooth to inspect history or update conditions.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-[11px] font-medium text-slate-600">
          {[
            { label: 'Healthy', color: '#10b981' },
            { label: 'Caries', color: '#ef4444' },
            { label: 'Filled', color: '#3b82f6' },
            { label: 'Crown', color: '#f59e0b' },
            { label: 'Root Canal', color: '#8b5cf6' },
            { label: 'Missing', color: '#94a3b8' },
            { label: 'Extraction', color: '#dc2626' },
            { label: 'Fracture', color: '#ea580c' },
          ].map((l) => (
            <div key={l.label} className="flex items-center gap-1.5 px-2 py-1 bg-slate-50 border border-slate-200 rounded-md">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: l.color }} />
              <span>{l.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Arch Dental Grid */}
      <div className="min-w-[700px] flex flex-col gap-6">
        {/* UPPER JAW (Maxilla) */}
        <div>
          <div className="text-center text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Maxilla (Upper Jaw)
          </div>
          <div className="flex items-center justify-center gap-4 bg-slate-50/70 p-4 rounded-xl border border-slate-100">
            {/* Quadrant 1 (18 -> 11) */}
            <div className="flex items-center gap-1">
              {q1.map((tNum) => (
                <ToothGraphic
                  key={tNum}
                  toothNumber={tNum}
                  conditionData={teeth[tNum]}
                  isSelected={selectedTooth === tNum}
                  onClick={() => onSelectTooth(tNum)}
                />
              ))}
            </div>

            {/* Midline Divider */}
            <div className="w-px h-20 bg-slate-300 mx-1 flex flex-col items-center justify-center text-[10px] font-bold text-slate-400">
              MID
            </div>

            {/* Quadrant 2 (21 -> 28) */}
            <div className="flex items-center gap-1">
              {q2.map((tNum) => (
                <ToothGraphic
                  key={tNum}
                  toothNumber={tNum}
                  conditionData={teeth[tNum]}
                  isSelected={selectedTooth === tNum}
                  onClick={() => onSelectTooth(tNum)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Horizontal Occlusal Plane Separator */}
        <div className="flex items-center gap-4 px-4">
          <div className="flex-1 h-px bg-slate-200" />
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Occlusal Plane
          </span>
          <div className="flex-1 h-px bg-slate-200" />
        </div>

        {/* LOWER JAW (Mandible) */}
        <div>
          <div className="flex items-center justify-center gap-4 bg-slate-50/70 p-4 rounded-xl border border-slate-100">
            {/* Quadrant 4 (48 -> 41) */}
            <div className="flex items-center gap-1">
              {q4.map((tNum) => (
                <ToothGraphic
                  key={tNum}
                  toothNumber={tNum}
                  conditionData={teeth[tNum]}
                  isSelected={selectedTooth === tNum}
                  onClick={() => onSelectTooth(tNum)}
                />
              ))}
            </div>

            {/* Midline Divider */}
            <div className="w-px h-20 bg-slate-300 mx-1 flex flex-col items-center justify-center text-[10px] font-bold text-slate-400">
              MID
            </div>

            {/* Quadrant 3 (31 -> 38) */}
            <div className="flex items-center gap-1">
              {q3.map((tNum) => (
                <ToothGraphic
                  key={tNum}
                  toothNumber={tNum}
                  conditionData={teeth[tNum]}
                  isSelected={selectedTooth === tNum}
                  onClick={() => onSelectTooth(tNum)}
                />
              ))}
            </div>
          </div>
          <div className="text-center text-xs font-bold uppercase tracking-wider text-slate-400 mt-2">
            Mandible (Lower Jaw)
          </div>
        </div>
      </div>
    </div>
  );
};
