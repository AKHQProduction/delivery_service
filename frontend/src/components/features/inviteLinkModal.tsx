import React, { useState } from "react";

interface InviteLinkModalProps {
  link: string;
  onClose: () => void;
}

export const InviteLinkModal: React.FC<InviteLinkModalProps> = ({
  link,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <div className="fixed inset-0 flex items-center justify-center px-4 z-9999 bg-black/50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Запрошення створено</h2>

        <label className="text-sm text-gray-500">Share Link</label>
        <textarea
          value={link}
          readOnly
          title="Share Link"
          className="w-full p-3 border rounded-xl mt-2 text-sm bg-gray-50"
          rows={3}
        />

        <p className="text-xs text-gray-400 mt-2">Діє 24 години, одноразова</p>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleCopy}
            className={`flex-1 py-4 rounded-2xl border transition-all duration-300 ${
              copied
                ? "bg-gray-600 text-white scale-105"
                : "bg-white text-black"
            }`}
          >
            {copied ? "Copied!" : "Copy"}
          </button>

          <a
            href={link}
            target="_blank"
            className="flex-1 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-2xl transition-colors text-center"
          >
            Share
          </a>
        </div>

        <button className="mt-4 text-sm text-gray-400 w-full" onClick={onClose}>
          Закрити
        </button>
      </div>
    </div>
  );
};
