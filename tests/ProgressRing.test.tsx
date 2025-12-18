import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ProgressRing } from '../src/components/ProgressRing';

describe('ProgressRing', () => {
  it('renders value and max correctly', () => {
    render(<ProgressRing value={15} max={20} />);
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('/20')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<ProgressRing value={10} max={25} label="Lifte" />);
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('Lifte')).toBeInTheDocument();
  });

  it('renders with label and unit', () => {
    render(<ProgressRing value={45} max={100} label="Pisten" unit="km" />);
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('Pisten (km)')).toBeInTheDocument();
  });

  it('handles zero max value gracefully', () => {
    render(<ProgressRing value={0} max={0} />);
    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('/0')).toBeInTheDocument();
  });

  it('renders SVG elements for the ring', () => {
    const { container } = render(<ProgressRing value={50} max={100} />);
    const circles = container.querySelectorAll('circle');
    expect(circles.length).toBe(2);
  });
});
