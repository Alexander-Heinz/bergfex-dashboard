import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SortControls } from '../src/components/SortControls';

describe('SortControls', () => {
  const mockOnSortChange = vi.fn();

  it('renders all sort options', () => {
    render(<SortControls currentSort="snowMountain" onSortChange={mockOnSortChange} />);
    
    expect(screen.getByText('Schneehöhe')).toBeInTheDocument();
    expect(screen.getByText('Neuschnee')).toBeInTheDocument();
    expect(screen.getByText('Pisten km')).toBeInTheDocument();
    expect(screen.getByText('Lifte')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
  });

  it('renders "Sortieren nach:" label', () => {
    render(<SortControls currentSort="snowMountain" onSortChange={mockOnSortChange} />);
    expect(screen.getByText('Sortieren nach:')).toBeInTheDocument();
  });

  it('calls onSortChange when a sort option is clicked', () => {
    render(<SortControls currentSort="snowMountain" onSortChange={mockOnSortChange} />);
    
    fireEvent.click(screen.getByText('Neuschnee'));
    expect(mockOnSortChange).toHaveBeenCalledWith('newSnow');
  });

  it('calls onSortChange with correct value for each option', () => {
    render(<SortControls currentSort="name" onSortChange={mockOnSortChange} />);
    
    fireEvent.click(screen.getByText('Pisten km'));
    expect(mockOnSortChange).toHaveBeenCalledWith('slopesOpenKm');

    fireEvent.click(screen.getByText('Lifte'));
    expect(mockOnSortChange).toHaveBeenCalledWith('liftsOpen');
  });
});
