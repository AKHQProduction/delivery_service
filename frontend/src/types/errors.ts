/**
 * Standard API error response structure
 */
export interface ApiError {
  status: number;
  code: string;
  message: string;
  details?: unknown;
}

/**
 * Known error codes from the API
 */
export const ApiErrorCode = {
  DUPLICATE_PHONES: "duplicate_phones",
  NOT_FOUND: "not_found",
  UNAUTHORIZED: "unauthorized",
  FORBIDDEN: "forbidden",
  VALIDATION_ERROR: "validation_error",
  INTERNAL_ERROR: "internal_error",
} as const;

export type ApiErrorCode = typeof ApiErrorCode[keyof typeof ApiErrorCode];

/**
 * Duplicate phone error details
 */
export interface DuplicatePhoneError extends ApiError {
  code: typeof ApiErrorCode.DUPLICATE_PHONES;
  details: {
    duplicates: Array<{
      phone: string;
      clientId: string;
      clientName: string;
    }>;
  };
}

/**
 * Validation error details
 */
export interface ValidationError extends ApiError {
  code: typeof ApiErrorCode.VALIDATION_ERROR;
  details: {
    field: string;
    constraint: string;
  }[];
}

/**
 * Type guard to check if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    "code" in error &&
    "message" in error
  );
}

/**
 * Type guard for duplicate phone errors
 */
export function isDuplicatePhoneError(
  error: unknown
): error is DuplicatePhoneError {
  return (
    isApiError(error) &&
    error.code === ApiErrorCode.DUPLICATE_PHONES &&
    typeof error.details === "object" &&
    error.details !== null &&
    "duplicates" in error.details
  );
}

/**
 * Type guard for validation errors
 */
export function isValidationError(error: unknown): error is ValidationError {
  return (
    isApiError(error) &&
    error.code === ApiErrorCode.VALIDATION_ERROR &&
    Array.isArray((error as ValidationError).details)
  );
}
