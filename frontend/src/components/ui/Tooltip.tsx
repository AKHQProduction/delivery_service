interface TooltipProps {
  type?: "info" | "success";
  title?: string;
  message: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  type = "info",
  title,
  message,
}) => {
  const iconPaths = {
    info: `M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0
      1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 
      0 100-2v-3a1 1 0 00-1-1H9z`,
    success: `M10 18a8 8 0 100-16 8 8 0 000 
      16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 
      7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 
      001.414 0l4-4z`,
  };

  const config = {
    info: {
      container: "bg-blue-50 border-blue-100",
      icon: "text-blue-600",
      text: "text-blue-700",
      title: "text-blue-900",
      defaultTitle: "Підказка",
    },
    success: {
      container: "bg-green-50 border-green-100",
      icon: "text-green-600",
      text: "text-green-700",
      title: "text-green-900",
      defaultTitle: "Все готово!",
    },
  }[type];

  return (
    <div className={`p-4 rounded-xl flex gap-3 border ${config.container}`}>
      <svg
        className={`w-5 h-5 shrink-0 mt-0.5 ${config.icon}`}
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path fillRule="evenodd" clipRule="evenodd" d={iconPaths[type]} />
      </svg>

      <div className="text-sm">
        <p className={`font-medium mb-1 ${config.title}`}>
          {title ?? config.defaultTitle}
        </p>
        <p className={config.text}>{message}</p>
      </div>
    </div>
  );
};
