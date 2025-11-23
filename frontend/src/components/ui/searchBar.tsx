import SearchIcon from "../../assets/icons/search.svg";
type SearchBarProps = {
  placeholder: string;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
};

export const SearchBar = ({
  placeholder,
  searchTerm,
  setSearchTerm,
}: SearchBarProps) => {
  return (
    <div className="px-6 pb-6">
      <div className="relative">
        <img
          src={SearchIcon}
          alt="Search"
          className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
        />
        <input
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-white  rounded-xl text-base placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>
  );
};
