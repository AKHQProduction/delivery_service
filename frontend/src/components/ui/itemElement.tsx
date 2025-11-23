type ItemElementProps = {
  descriptionText: string;
  elementText: string;
};

export const ItemElement = ({
  descriptionText,
  elementText,
}: ItemElementProps) => {
  return (
    <div className="space-y-3 mb-4">
      <div className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
        <p className="text-sm text-gray-500 mb-1">{descriptionText}</p>
        <p className="text-base font-semibold">{elementText}</p>
      </div>
    </div>
  );
};
