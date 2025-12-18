import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SnowDepthGauge } from '../src/components/SnowDepthGauge';

describe('SnowDepthGauge', () => {
  it('renders valley and mountain snow depths', () => {
    render(<SnowDepthGauge valley={35} mountain={150} />);
    expect(screen.getByText('35 cm')).toBeInTheDocument();
    expect(screen.getByText('150 cm')).toBeInTheDocument();
  });

  it('renders labels for valley and mountain', () => {
    render(<SnowDepthGauge valley={20} mountain={100} />);
    expect(screen.getByText('Tal')).toBeInTheDocument();
    expect(screen.getByText('Berg')).toBeInTheDocument();
  });

  it('handles zero values', () => {
    render(<SnowDepthGauge valley={0} mountain={0} />);
    expect(screen.getByText('0 cm')).toBeInTheDocument();
  });

  it('renders icons for valley and mountain', () => {
    const { container } = render(<SnowDepthGauge valley={50} mountain={200} />);
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThanOrEqual(2);
  });
});
