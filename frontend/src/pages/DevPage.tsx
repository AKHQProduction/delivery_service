import { useState } from "react";
import { useUserStore } from "../context/useUserStore";
import { getUser } from "../services/userService";

export const DevPage = () => {
  const [userID, setUserID] = useState<string>("");

  const handleSetUserID = async () => {
    localStorage.setItem("userID", userID);
    const data = await getUser();
    useUserStore.getState().setUser({
      user_id: data.user_id,
      role: data.role,
    });
    window.location.reload();
  };

  return (
    <>
      <div className="flex flex-col items-center m-5 p-5 border bg-white  border-gray-300 rounded-lg gap-4">
        <p className="text-2xl b">Dev Page</p>
        <ul>
          <li>Owner User (telegram_id: 1000)</li>
          <li>Manager User (telegram_id: 2000)</li>
          <li>Courier User (telegram_id: 3000)</li>
        </ul>
        <div className="relative">
          <input
            type="text"
            className="bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md pl-3 pr-16 py-2 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-300 shadow-sm focus:shadow"
            placeholder="Enter User ID"
            onChange={(e) => setUserID(e.target.value)}
          />
          <button
            className="absolute right-1 top-1 rounded bg-slate-800 py-1 px-2.5 border border-transparent text-center text-sm text-white transition-all shadow-sm hover:shadow focus:bg-slate-700 focus:shadow-none active:bg-slate-700 hover:bg-slate-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
            type="button"
            onClick={() => {
              handleSetUserID();
            }}
          >
            Submit
          </button>
        </div>
      </div>
    </>
  );
};
