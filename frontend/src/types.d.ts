interface MapComponentProps {
    generateRoute: (
      mapInstance: L.Map,
      setRouteControl: React.Dispatch<React.SetStateAction<L.Routing.Control | null>>
    ) => void;
  }