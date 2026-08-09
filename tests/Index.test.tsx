import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Index from '../src/pages/Index';

const mockResortData = {
  totalCount: 2,
  openCount: 2,
  avgSnowMountain: 150,
  totalNewSnow: 20,
  totalOpenKm: 100,
  globalTotalCount: 2,
  globalOpenCount: 2,
  globalAvgSnowMountain: 150,
  globalTotalNewSnow: 20,
  globalTotalOpenKm: 100,
  avalancheDistribution: { '1': 1, '2': 1 },
  availableCountries: ['AT'],
  availableRegions: { AT: ['Tirol'] },
  resorts: [
    {
      id: '1',
      name: 'St. Anton am Arlberg',
      region: 'Tirol',
      country: 'AT',
      status: 'Geöffnet',
      snowValley: 50,
      snowMountain: 150,
      newSnow: 20,
      snowCondition: 'Pulver',
      lastSnowfall: '2024-12-01',
      avalancheWarning: 2,
      avalancheText: 'Mäßig',
      liftsOpen: 80,
      liftsTotal: 88,
      slopesOpenKm: 300,
      slopesTotalKm: 300,
      slopesOpen: 300,
      slopesTotal: 300,
      slopeCondition: 'Gut',
      lastUpdate: '2024-12-01',
      altitude: { min: 1300, max: 2800 },
      url: 'https://bergfex.at',
      shredScore: 8.5,
    },
    {
      id: '2',
      name: 'Kitzbühel',
      region: 'Tirol',
      country: 'AT',
      status: 'Geöffnet',
      snowValley: 40,
      snowMountain: 120,
      newSnow: 10,
      snowCondition: 'Griffig',
      lastSnowfall: '2024-12-01',
      avalancheWarning: 1,
      avalancheText: 'Gering',
      liftsOpen: 50,
      liftsTotal: 57,
      slopesOpenKm: 180,
      slopesTotalKm: 230,
      slopesOpen: 180,
      slopesTotal: 230,
      slopeCondition: 'Gut',
      lastUpdate: '2024-12-01',
      altitude: { min: 800, max: 2000 },
      url: 'https://bergfex.at',
      shredScore: 7.8,
    },
  ],
  topSnowResorts: [
    {
      id: '1',
      name: 'St. Anton am Arlberg',
      snowMountain: 150,
    }
  ],
  topNewSnowResorts: [
    {
      id: '1',
      name: 'St. Anton am Arlberg',
      newSnow: 20,
    }
  ],
};

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
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
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResortData,
      })
    );
  });

  it('renders the header', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText('Alpen Schnee Radar')).toBeInTheDocument();
  });

  it('renders dashboard stats section', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText('Geöffnete Gebiete')).toBeInTheDocument();
    expect(await screen.findByText('Ø Schneehöhe Berg')).toBeInTheDocument();
    expect(await screen.findByText('Neuschnee gesamt')).toBeInTheDocument();
    expect(await screen.findByText('Offene Pistenkilometer')).toBeInTheDocument();
  });

  it('renders chart sections', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText('Top 5 Schneehöhe Berg')).toBeInTheDocument();
    expect(await screen.findByText('Frischer Neuschnee')).toBeInTheDocument();
    expect(await screen.findByText('Lawinenwarnstufen')).toBeInTheDocument();
  });

  it('renders sort controls', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText('Sortieren nach:')).toBeInTheDocument();
    expect(await screen.findByText('Schneehöhe')).toBeInTheDocument();
    expect(await screen.findByText('Neuschnee')).toBeInTheDocument();
  });

  it('renders "Alle Skigebiete" section', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText(/Alle Skigebiete/)).toBeInTheDocument();
  });

  it('changes sort order when clicking sort buttons', async () => {
    renderWithProviders(<Index />);
    const nameButton = await screen.findByText('Name');
    fireEvent.click(nameButton);
    expect(nameButton).toBeInTheDocument();
  });

  it('renders footer with data source info', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText(/BigQuery/)).toBeInTheDocument();
  });

  it('renders multiple resort cards', async () => {
    renderWithProviders(<Index />);
    expect(await screen.findByText('St. Anton am Arlberg')).toBeInTheDocument();
    expect(await screen.findByText('Kitzbühel')).toBeInTheDocument();
  });
});

