/**
 * Converts a date string from DD.MM.YYYY format to ISO format (YYYY-MM-DD)
 * for use with HTML date inputs
 *
 * @param dateStr - Date string in DD.MM.YYYY format or already in YYYY-MM-DD format
 * @returns Date string in YYYY-MM-DD format, or empty string if input is invalid
 */
export const convertDateToISO = (dateStr: string): string => {
  if (!dateStr) return "";

  // Check if already in ISO format (YYYY-MM-DD)
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;

  // Convert from DD.MM.YYYY to YYYY-MM-DD
  const parts = dateStr.split(".");
  if (parts.length === 3) {
    return `${parts[2]}-${parts[1]}-${parts[0]}`;
  }

  return dateStr;
};

/**
 * Converts a date string from ISO format (YYYY-MM-DD) to DD.MM.YYYY format
 * for display purposes
 *
 * @param dateStr - Date string in YYYY-MM-DD format
 * @returns Date string in DD.MM.YYYY format, or empty string if input is invalid
 */
export const convertISOToDisplayDate = (dateStr: string): string => {
  if (!dateStr) return "";

  // Check if in ISO format (YYYY-MM-DD)
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    const parts = dateStr.split("-");
    if (parts.length === 3) {
      return `${parts[2]}.${parts[1]}.${parts[0]}`;
    }
  }

  return dateStr;
};

export const formatLocalDateKey = (date: Date = new Date()): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export const addDaysToDateKey = (dateKey: string, days: number): string => {
  const date = new Date(`${dateKey}T00:00:00`);
  date.setDate(date.getDate() + days);
  return formatLocalDateKey(date);
};
