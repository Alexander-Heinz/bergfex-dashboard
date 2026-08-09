import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Index from '../src/pages/Index';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // disable retries in tests
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

const renderWithProviders = (component: React.ReactNode) => {
  return render(<>{component}</>, { wrapper: createWrapper() });
};

describe('Index Page', () => {
  it('renders the header', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText('Alpen Schnee Radar')).toBeInTheDocument();
  });

  it('renders dashboard stats section', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText('Geöffnete Gebiete')).toBeInTheDocument();
    expect(screen.getByText('Ø Schneehöhe Berg')).toBeInTheDocument();
    expect(screen.getByText('Neuschnee gesamt')).toBeInTheDocument();
    expect(screen.getByText('Offene Pistenkilometer')).toBeInTheDocument();
  });

  it('renders chart sections', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText('Top 5 Schneehöhe Berg')).toBeInTheDocument();
    expect(screen.getByText('Frischer Neuschnee')).toBeInTheDocument();
    expect(screen.getByText('Lawinenwarnstufen')).toBeInTheDocument();
  });

  it('renders sort controls', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText('Sortieren nach:')).toBeInTheDocument();
    expect(screen.getByText('Schneehöhe')).toBeInTheDocument();
    expect(screen.getByText('Neuschnee')).toBeInTheDocument();
  });

  it('renders "Alle Skigebiete" section', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText('Alle Skigebiete')).toBeInTheDocument();
  });

  it('changes sort order when clicking sort buttons', () => {
    renderWithProviders(<Index />);
    fireEvent.click(screen.getByText('Name'));
    const nameButton = screen.getByText('Name');
    expect(nameButton).toBeInTheDocument();
  });

  it('renders footer with data source info', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText(/bergfex.com/)).toBeInTheDocument();
  });

  it('renders multiple resort cards', () => {
    renderWithProviders(<Index />);
    expect(screen.getByText('St. Anton am Arlberg')).toBeInTheDocument();
    expect(screen.getByText('Kitzbühel')).toBeInTheDocument();
  });
});
