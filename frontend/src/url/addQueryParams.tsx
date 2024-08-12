import { Link } from "react-router-dom";

export const AddQueryParams: React.FC<QueryParams> = ({ pathname, search }) => {
  return (
    <Link
      to={{
        pathname: pathname,
        search: search,
      }}
    ></Link>
  );
};
