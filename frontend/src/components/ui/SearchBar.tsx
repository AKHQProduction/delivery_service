import SearchIcon from "../../assets/icons/search.svg";

type SearchBarProps = {
  placeholder: string;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
};

export const SearchBar = ({ placeholder, searchTerm, setSearchTerm }: SearchBarProps) => {
  return (
    <>
      <div className="relative">
        <img
          src={SearchIcon}
          alt="Search"
          className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 opacity-55"
        />
        <input
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="h-10 w-full rounded-md border border-slate-300 bg-white pl-9 pr-3 text-sm leading-5 text-slate-950 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
      </div>
    </>
  );
};
