type Coordinates = {
    latitude: number;
    longitude: number;
  };
  
export const getUserCoordinates = (): Promise<Coordinates> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocation is not supported by your browser."));
      } else {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            resolve({ latitude, longitude });
          },
          (error) => {
            reject(new Error(`Geolocation error: ${error.message}`));
          }
        );
      }
    });
  }