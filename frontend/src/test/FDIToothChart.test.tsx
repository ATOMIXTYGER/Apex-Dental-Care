import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FDIToothChart, getConditionColor } from '../components/dental/FDIToothChart';
import { ToothCondition } from '../types';

describe('FDIToothChart Component', () => {
  const mockTeeth: Record<number, ToothCondition> = {
    11: { id: 1, patient_id: 1, tooth_number: 11, condition: 'healthy', current_condition: 'healthy', updated_at: '2026-01-01' },
    16: { id: 2, patient_id: 1, tooth_number: 16, condition: 'caries', current_condition: 'caries', severity: 'moderate', updated_at: '2026-01-01' },
    21: { id: 3, patient_id: 1, tooth_number: 21, condition: 'filled', current_condition: 'filled', updated_at: '2026-01-01' },
    36: { id: 4, patient_id: 1, tooth_number: 36, condition: 'root_canal', current_condition: 'root_canal', updated_at: '2026-01-01' },
    48: { id: 5, patient_id: 1, tooth_number: 48, condition: 'missing', current_condition: 'missing', updated_at: '2026-01-01' },
  };

  it('renders anatomical jaws (Maxilla and Mandible)', () => {
    render(
      <FDIToothChart
        teeth={mockTeeth}
        selectedTooth={null}
        onSelectTooth={() => {}}
      />
    );

    expect(screen.getByText(/Maxilla \(Upper Jaw\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Mandible \(Lower Jaw\)/i)).toBeInTheDocument();
  });

  it('renders key permanent teeth from 11 to 48', () => {
    render(
      <FDIToothChart
        teeth={mockTeeth}
        selectedTooth={null}
        onSelectTooth={() => {}}
      />
    );

    // Verify presence of tooth labels
    expect(screen.getByText('11')).toBeInTheDocument();
    expect(screen.getByText('18')).toBeInTheDocument();
    expect(screen.getByText('21')).toBeInTheDocument();
    expect(screen.getByText('28')).toBeInTheDocument();
    expect(screen.getByText('31')).toBeInTheDocument();
    expect(screen.getByText('38')).toBeInTheDocument();
    expect(screen.getByText('41')).toBeInTheDocument();
    expect(screen.getByText('48')).toBeInTheDocument();
  });

  it('triggers onSelectTooth when a tooth is clicked', () => {
    const handleSelectTooth = vi.fn();
    render(
      <FDIToothChart
        teeth={mockTeeth}
        selectedTooth={null}
        onSelectTooth={handleSelectTooth}
      />
    );

    const tooth16 = screen.getByText('16').closest('div');
    expect(tooth16).toBeTruthy();
    if (tooth16) fireEvent.click(tooth16);

    expect(handleSelectTooth).toHaveBeenCalledWith(16);
  });

  it('maps dental clinical conditions to their correct medical color codes', () => {
    expect(getConditionColor('healthy')).toBe('#10b981');
    expect(getConditionColor('caries')).toBe('#ef4444');
    expect(getConditionColor('filled')).toBe('#3b82f6');
    expect(getConditionColor('crown')).toBe('#f59e0b');
    expect(getConditionColor('root_canal')).toBe('#8b5cf6');
    expect(getConditionColor('missing')).toBe('#94a3b8');
  });
});
