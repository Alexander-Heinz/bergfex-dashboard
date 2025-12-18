import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '../src/components/StatusBadge';

describe('StatusBadge', () => {
  it('renders "Geöffnet" status correctly', () => {
    render(<StatusBadge status="Geöffnet" />);
    expect(screen.getByText('Geöffnet')).toBeInTheDocument();
  });

  it('renders "Geschlossen" status correctly', () => {
    render(<StatusBadge status="Geschlossen" />);
    expect(screen.getByText('Geschlossen')).toBeInTheDocument();
  });

  it('renders "Teilweise geöffnet" status correctly', () => {
    render(<StatusBadge status="Teilweise geöffnet" />);
    expect(screen.getByText('Teilweise geöffnet')).toBeInTheDocument();
  });

  it('has correct styling classes for open status', () => {
    const { container } = render(<StatusBadge status="Geöffnet" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('text-status-open');
  });

  it('has correct styling classes for closed status', () => {
    const { container } = render(<StatusBadge status="Geschlossen" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('text-status-closed');
  });
});
