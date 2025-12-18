import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AvalancheBadge } from '../src/components/AvalancheBadge';

describe('AvalancheBadge', () => {
  it('renders avalanche level and text', () => {
    render(<AvalancheBadge level={2} text="Mäßig" />);
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('- Mäßig')).toBeInTheDocument();
  });

  it('renders compact version correctly', () => {
    render(<AvalancheBadge level={3} text="Erheblich" compact />);
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.queryByText('- Erheblich')).not.toBeInTheDocument();
  });

  it('applies correct styling for level 1 (low)', () => {
    const { container } = render(<AvalancheBadge level={1} text="Gering" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('text-avalanche-low');
  });

  it('applies correct styling for level 3 (considerable)', () => {
    const { container } = render(<AvalancheBadge level={3} text="Erheblich" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('text-avalanche-considerable');
  });

  it('applies correct styling for level 5 (extreme)', () => {
    const { container } = render(<AvalancheBadge level={5} text="Sehr groß" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('text-avalanche-extreme');
  });
});
