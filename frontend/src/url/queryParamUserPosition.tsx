import { AddQueryParams } from "./addQueryParams";

export const UserPositionQueryParam: React.FC = () => {
  const query = `latitude=&longitude=`;

  return (
    <>
      <AddQueryParams pathname="/" search={query} />
    </>
  );
};

export const queryParamsCoordinates = () => {
  let params = new URLSearchParams(document.location.search);

  try {
    let latitude = parseFloat(params.get("latitude") || "");
    let longitude = parseFloat(params.get("longitude") || "");

    return [longitude, latitude] as [number, number];
  } catch (err) {
    console.log("error", err);
    return null;
  }
};
