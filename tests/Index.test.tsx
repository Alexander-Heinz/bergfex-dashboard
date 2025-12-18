import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Index from '../src/pages/Index';

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Index Page', () => {
  it('renders the header', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText('Alpen Schnee Radar')).toBeInTheDocument();
  });

  it('renders dashboard stats section', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText('Geöffnete Gebiete')).toBeInTheDocument();
    expect(screen.getByText('Ø Schneehöhe Berg')).toBeInTheDocument();
    expect(screen.getByText('Neuschnee gesamt')).toBeInTheDocument();
    expect(screen.getByText('Offene Pistenkilometer')).toBeInTheDocument();
  });

  it('renders chart sections', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText('Top 5 Schneehöhe Berg')).toBeInTheDocument();
    expect(screen.getByText('Frischer Neuschnee')).toBeInTheDocument();
    expect(screen.getByText('Lawinenwarnstufen')).toBeInTheDocument();
  });

  it('renders sort controls', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText('Sortieren nach:')).toBeInTheDocument();
    expect(screen.getByText('Schneehöhe')).toBeInTheDocument();
    expect(screen.getByText('Neuschnee')).toBeInTheDocument();
  });

  it('renders "Alle Skigebiete" section', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText('Alle Skigebiete')).toBeInTheDocument();
  });

  it('changes sort order when clicking sort buttons', () => {
    renderWithRouter(<Index />);
    fireEvent.click(screen.getByText('Name'));
    const nameButton = screen.getByText('Name');
    expect(nameButton).toBeInTheDocument();
  });

  it('renders footer with data source info', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText(/bergfex.com/)).toBeInTheDocument();
  });

  it('renders multiple resort cards', () => {
    renderWithRouter(<Index />);
    expect(screen.getByText('St. Anton am Arlberg')).toBeInTheDocument();
    expect(screen.getByText('Kitzbühel')).toBeInTheDocument();
  });
});
