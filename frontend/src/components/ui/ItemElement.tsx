type ItemElementProps = {
  descriptionText: string;
  elementText: string;
  comment?: string;
};

export const ItemElement = ({ descriptionText, elementText, comment }: ItemElementProps) => {
  return (
    <div className="mb-4">
      <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-5 border border-gray-200 shadow-sm">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
          {descriptionText}
        </p>
        <p className="text-base font-semibold text-gray-900 leading-relaxed">{elementText}</p>

        {comment && comment.trim() !== "" && (
          <div className="mt-4 relative">
            <div className="relative bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 border-l-4 border-amber-400 rounded-r-2xl pl-5 pr-4 py-4 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold text-amber-900 uppercase tracking-wider">
                      Примітка
                    </span>
                  </div>
                  <p className="text-sm text-amber-950 leading-relaxed font-medium ">{comment}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
