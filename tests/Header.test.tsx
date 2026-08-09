import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Header } from '../src/components/Header';

describe('Header', () => {
  it('renders the main title', () => {
    render(<Header resortCount={10} latestDate="2024-12-01" />);
    expect(screen.getByText('Alpen Schnee Radar')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<Header resortCount={10} latestDate="2024-12-01" />);
    expect(
      screen.getByText('Live Schneebericht für Skigebiete in den Alpen')
    ).toBeInTheDocument();
  });

  it('renders quick stats pills', () => {
    render(<Header resortCount={10} latestDate="2024-12-01" />);
    expect(screen.getByText('10 Geöffnete Skigebiete')).toBeInTheDocument();
    expect(screen.getByText(/Aktuell:/)).toBeInTheDocument();
  });

  it('renders as a header element', () => {
    const { container } = render(<Header resortCount={10} latestDate="2024-12-01" />);
    expect(container.querySelector('header')).toBeInTheDocument();
  });

  it('contains mountain icon', () => {
    const { container } = render(<Header resortCount={10} latestDate="2024-12-01" />);
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThan(0);
  });
});
