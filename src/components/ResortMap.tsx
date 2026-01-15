import { useState, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { SkiResort } from '../types/resort';
import L from 'leaflet';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

// Custom Marker CSS is handled via inline styles in the divIcon html for simplicity in this environment,
// or we could add it to index.css. Using Tailwind classes in the HTML string.

type MapMetric = 'snowMountain' | 'newSnow';

interface ResortMapProps {
  resorts: SkiResort[];
}

const ResortMap = ({ resorts }: ResortMapProps) => {
  const [metric, setMetric] = useState<MapMetric>('snowMountain');
  const [minVal, setMinVal] = useState<number>(0);

  // Reset filter when toggling between metrics
  useEffect(() => {
    setMinVal(0);
  }, [metric]);

  // Default center (focus on Alps)
  const defaultCenter: [number, number] = [47.5, 13.0];
  const defaultZoom = 7;

  // Filter and prepare display data
  const filteredResorts = useMemo(() => {
    return resorts.filter((r) => {
      const val = metric === 'snowMountain' ? (r.snowMountain || 0) : (r.newSnow || 0);
      return r.latitude && r.longitude && val >= minVal;
    });
  }, [resorts, metric, minVal]);

  // Color logic
  const getMarkerColor = (val: number, currentMetric: MapMetric) => {
    if (currentMetric === 'snowMountain') {
      if (val >= 200) return '#4c1d95'; // Purple-900
      if (val >= 150) return '#1e40af'; // Blue-800
      if (val >= 100) return '#2563eb'; // Blue-600
      if (val >= 50) return '#60a5fa';  // Blue-400
      if (val > 0) return '#93c5fd';   // Blue-300
      return '#94a3b8'; // Slate-400
    } else { // newSnow
      if (val >= 30) return '#7e22ce'; // Purple-700
      if (val >= 15) return '#2563eb'; // Blue-600
      if (val >= 5) return '#3b82f6';  // Blue-500
      if (val > 0) return '#93c5fd';   // Blue-300
      return '#cbd5e1'; // Slate-300
    }
  };

  const createCustomIcon = (val: number, currentMetric: MapMetric) => {
    const color = getMarkerColor(val, currentMetric);
    const size = val > 0 ? (metric === 'newSnow' ? 32 : 36) : 28;
    
    return L.divIcon({
      className: 'custom-div-icon',
      html: `
        <div style="
          background-color: ${color};
          width: ${size}px;
          height: ${size}px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          color: white;
          font-weight: bold;
          font-size: ${size > 30 ? '12px' : '10px'};
        ">
          <span style="transform: rotate(45deg);">${val}</span>
        </div>
      `,
      iconSize: [size, size],
      iconAnchor: [size / 2, size],
    });
  };

  return (
    <div className="relative w-full h-[700px] rounded-xl overflow-hidden shadow-xl border border-border group">
      {/* Map Content Toggle & Filter Overlay */}
      <div className="absolute top-4 right-4 z-[1000] bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 p-4 rounded-xl shadow-2xl border border-border flex flex-col gap-4 min-w-[200px]">
        <div className="space-y-2">
          <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground px-1">Ansicht</Label>
          <div className="flex bg-secondary p-1 rounded-lg gap-1">
            <button
              onClick={() => setMetric('snowMountain')}
              className={`flex-1 py-1 px-2 rounded-md text-xs font-medium transition-all ${
                metric === 'snowMountain' ? 'bg-background shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Gesamtschnee
            </button>
            <button
              onClick={() => setMetric('newSnow')}
              className={`flex-1 py-1 px-2 rounded-md text-xs font-medium transition-all ${
                metric === 'newSnow' ? 'bg-background shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Neuschnee
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground px-1">Min. {metric === 'snowMountain' ? 'Schnee' : 'Neuschnee'} (cm)</Label>
          <Select value={minVal.toString()} onValueChange={(v) => setMinVal(parseInt(v))}>
            <SelectTrigger className="h-9 text-xs">
              <SelectValue placeholder="Minimum..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0">Alle Gebiete</SelectItem>
              {metric === 'snowMountain' ? (
                <>
                  <SelectItem value="50">Ab 50 cm</SelectItem>
                  <SelectItem value="100">Ab 100 cm</SelectItem>
                  <SelectItem value="150">Ab 150 cm</SelectItem>
                  <SelectItem value="200">Ab 200 cm</SelectItem>
                </>
              ) : (
                <>
                  <SelectItem value="5">Ab 5 cm</SelectItem>
                  <SelectItem value="10">Ab 10 cm</SelectItem>
                  <SelectItem value="20">Ab 20 cm</SelectItem>
                  <SelectItem value="30">Ab 30 cm</SelectItem>
                </>
              )}
            </SelectContent>
          </Select>
        </div>
        
        <div className="pt-2 border-t border-border mt-1">
          <span className="text-[10px] text-muted-foreground">Zeige {filteredResorts.length} Gebiete</span>
        </div>
      </div>

      <MapContainer 
        center={defaultCenter} 
        zoom={defaultZoom} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {filteredResorts.map((resort) => {
          const val = metric === 'snowMountain' ? (resort.snowMountain || 0) : (resort.newSnow || 0);
          return (
            <Marker 
              key={resort.id} 
              position={[resort.latitude!, resort.longitude!]}
              icon={createCustomIcon(val, metric)}
            >
              <Popup className="resort-popup">
                <div className="p-3 min-w-[220px]">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-base leading-tight pr-2">{resort.name}</h3>
                    <Badge variant={resort.status === 'Geöffnet' ? 'default' : 'secondary'} className="text-[10px] h-5">
                      {resort.status}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 py-2 border-y border-border mb-3">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-muted-foreground uppercase font-bold">Berg</span>
                      <span className="text-sm font-semibold text-blue-600">{resort.snowMountain} cm</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-muted-foreground uppercase font-bold">Neuschnee</span>
                      <span className="text-sm font-semibold text-purple-600">{resort.newSnow} cm</span>
                    </div>
                  </div>

                  <div className="space-y-1 mb-3">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Talhöhe:</span>
                      <span className="font-medium">{resort.snowValley} cm</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Pisten:</span>
                      <span className="font-medium">{resort.slopesOpenKm} / {resort.slopesTotalKm} km</span>
                    </div>
                  </div>

                  <a 
                    href={resort.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-full inline-flex items-center justify-center rounded-md bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground shadow transition-colors hover:bg-primary/90"
                  >
                    Bergfex Details &rarr;
                  </a>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default ResortMap;
