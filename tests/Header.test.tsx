import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Header } from '../src/components/Header';

describe('Header', () => {
  it('renders the main title', () => {
    render(<Header />);
    expect(screen.getByText('Alpen Schnee Radar')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<Header />);
    expect(
      screen.getByText('Live Schneebericht für Skigebiete in Deutschland & Österreich')
    ).toBeInTheDocument();
  });

  it('renders quick stats pills', () => {
    render(<Header />);
    expect(screen.getByText('10 Skigebiete')).toBeInTheDocument();
    expect(screen.getByText('Aktuell: Dezember 2024')).toBeInTheDocument();
  });

  it('renders as a header element', () => {
    const { container } = render(<Header />);
    expect(container.querySelector('header')).toBeInTheDocument();
  });

  it('contains mountain icon', () => {
    const { container } = render(<Header />);
    const svgs = container.querySelectorAll('svg');
    expect(svgs.length).toBeGreaterThan(0);
  });
});
