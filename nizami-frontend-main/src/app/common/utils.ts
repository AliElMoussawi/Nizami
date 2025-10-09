import {HttpErrorResponse} from '@angular/common/http';

export function convertToFormData(data: any): FormData {
  const formData = new FormData();

  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      if (data[key] instanceof File) {
        formData.append(key, data[key]);
      } else if (typeof data[key] === 'object' && data[key] !== null) {
        formData.append(key, JSON.stringify(data[key]));
      } else {
        formData.append(key, data[key]);
      }
    }
  }

  return formData;
}


export function extractErrorFromResponse(error: any) {
  if (error instanceof HttpErrorResponse) {
    if (error.error?.error) {
      return error.error?.error;
    }

    if (error.status == 400) {
      return Object.values(error.error)[0] as string;
    }
  }

  return null;
}


export function detectLanguage(text: string): "ar" | "en" {
  let arabicCount = 0;
  let englishCount = 0;

  for (const char of text) {
    if (char >= '\u0600' && char <= '\u06FF') {
      arabicCount++;
    } else if ((char >= 'A' && char <= 'Z') || (char >= 'a' && char <= 'z')) {
      englishCount++;
    }
  }

  if (arabicCount > englishCount) {
    return "ar";
  } else if (englishCount > arabicCount) {
    return "en";
  } else if (arabicCount === englishCount && arabicCount !== 0) {
    return "ar";
  } else {
    return "ar";
  }
}
