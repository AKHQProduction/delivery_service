import React, { useState, useEffect, useRef } from 'react';
import { watchUserCoordinates } from '../api/getUserLocation';

export const WatchUserCoordinates: React.FC = () => {
  const [coordinates, setCoordinates] = useState<{ latitude: number; longitude: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const watchIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      return;
    }

    const handlePositionUpdate = (position: GeolocationPosition) => {
      const { latitude, longitude } = position.coords;
      setCoordinates({ latitude, longitude });
      setError(null);
    };

    const handleError = (error: GeolocationPositionError) => {
      setError(`Geolocation error: ${error.message}`);
      setCoordinates(null);
    };

    const watchId= watchUserCoordinates(handlePositionUpdate, handleError);
    watchIdRef.current = watchId;

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  return (
    <div>
      <button
        id="testBtn"
        onClick={() => {
          if (watchIdRef.current !== null) {
            navigator.geolocation.clearWatch(watchIdRef.current);
            watchIdRef.current = null;
          }
        }}
        className="absolute bg-blue-500 text-white p-2 rounded"
      >
        Stop Watching
      </button>
      {error && <p id="testBtn" className="absolute text-red-500">{error}</p>}
      {coordinates && (
        <p id="testBtn" className='absolute top-5 left-1/2 transform  bg-white'>
          Latitude: {coordinates.latitude}, Longitude: {coordinates.longitude}
        </p>
      )}
    </div>
  );
};
