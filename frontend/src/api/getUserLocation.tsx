// type Coordinates = {
//   latitude: number;
//   longitude: number;
// };

// export const getUserCoordinates = (): Promise<Coordinates> => {
//   return new Promise((resolve, reject) => {
//     if (!navigator.geolocation) {
//       reject(new Error("Geolocation is unable"));
//     } else {
//       navigator.geolocation.getCurrentPosition(
//         (position) => {
//           const { latitude, longitude } = position.coords;
//           resolve({ latitude, longitude });
//         },
//         (error) => {
//           reject(new Error(`Geolocation error: ${error.message}`));
//         }
//       );
//     }
//   });
// }; //<--- For future project enhancements

export const watchUserCoordinates = (
  onPositionUpdate: (position: GeolocationPosition) => void,
  onError: (error: GeolocationPositionError) => void
): number | null => {
  if (!navigator.geolocation) {
    onError({
      code: 0,
      message: "Geolocation is unable",
      PERMISSION_DENIED: 1,
      POSITION_UNAVAILABLE: 2,
      TIMEOUT: 3,
    } as GeolocationPositionError);
    return null;
  }

  return navigator.geolocation.watchPosition(onPositionUpdate, onError);
};

export const getCustomerPosition = async () => {
  try {
    const response = await fetch("/geocode", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    const routeData = await response.json();

    if (routeData.error) {
      alert("Address not found");
      return null;
    }

    const startCoords = [
      routeData.customer.latitude,
      routeData.customer.longitude,
    ];

    return startCoords;
  } catch (err) {
    console.log("error", err);
    return null;
  }
};
