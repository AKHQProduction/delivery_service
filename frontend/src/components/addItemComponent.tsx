export const AddItemComponent = () => {
  const handleClick = () => {
    console.log("Plus button clicked!");
    // Add your custom action here
  };

  return (
    <div className="fixed bottom-27 right-6">
      <div className="absolute inset-0 bg-indigo-600 rounded-full animate-ping opacity-75"></div>
      <button
        onClick={handleClick}
        className="relative w-14 h-14 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl transform hover:scale-105 active:scale-95"
        aria-label="Add new product"
      >
        <svg
          className="w-7 h-7 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          strokeWidth={2.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 4v16m8-8H4"
          />
        </svg>
      </button>
    </div>
  );
};
