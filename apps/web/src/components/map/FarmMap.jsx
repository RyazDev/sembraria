import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import { config, COLORS } from "@/config";

/**
 * Componente de mapa base con MapLibre.
 * - Mobile-first (altura configurable)
 * - Soporta marcadores, poligonos y centrado en bounds
 * - Dibujo basico de poligonos (futuro: mapbox-gl-draw)
 */
export default function FarmMap({
  center = config.map.defaultCenter,
  zoom = config.map.defaultZoom,
  height = "400px",
  polygons = [],
  onPolygonClick,
  className = "",
}) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          "raster-tiles": {
            type: "raster",
            tiles: [config.map.tilesUrl],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors © CARTO",
          },
        },
        layers: [
          {
            id: "raster-tiles",
            type: "raster",
            source: "raster-tiles",
            minzoom: 0,
            maxzoom: 22,
          },
        ],
      },
      center,
      zoom,
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");
    map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");

    map.on("load", () => {
      setLoaded(true);
    });

    mapRef.current = map;

    return () => map.remove();
  }, []);

  // Render polygons
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loaded) return;

    // Limpiar layers previos
    polygons.forEach((p, i) => {
      const id = `polygon-${i}`;
      if (map.getLayer(id)) map.removeLayer(id);
      if (map.getSource(id)) map.removeSource(id);

      if (p.coordinates) {
        map.addSource(id, {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: { type: "Polygon", coordinates: p.coordinates },
            properties: p.properties || {},
          },
        });
        map.addLayer({
          id,
          type: "fill",
          source: id,
          paint: {
            "fill-color": p.color || COLORS.action,
            "fill-opacity": 0.4,
          },
        });
        map.addLayer({
          id: `${id}-outline`,
          type: "line",
          source: id,
          paint: {
            "line-color": p.color || COLORS.action,
            "line-width": 2,
          },
        });

        if (onPolygonClick) {
          map.on("click", id, () => onPolygonClick(p));
        }
      }
    });
  }, [polygons, loaded, onPolygonClick]);

  return (
    <div
      ref={containerRef}
      style={{ height }}
      className={`w-full rounded-xl overflow-hidden border border-border/40 ${className}`}
    />
  );
}
