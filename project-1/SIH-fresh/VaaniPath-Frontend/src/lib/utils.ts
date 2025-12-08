import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const getErrorMessage = (error: any): string => {
  if (!error) return "An unknown error occurred";

  // Handle Axios response errors
  if (error.response?.data) {
    const data = error.response.data;

    // Handle Pydantic validation errors (array of objects)
    if (data.detail && Array.isArray(data.detail)) {
      return data.detail
        .map((err: any) => err.msg || "Invalid input")
        .join(", ");
    }

    // Handle string detail
    if (typeof data.detail === "string") {
      return data.detail;
    }

    // Handle value error (common in FastAPI)
    if (data.message) {
      return data.message;
    }
  }

  // Handle generic error message
  if (error.message) {
    return error.message;
  }

  return "An unexpected error occurred";
};
