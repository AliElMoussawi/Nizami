import {HttpErrorResponse} from '@angular/common/http';

/**
 * Attempts to extract a well-known subscription/user validation error key
 * returned by the backend and convert it to our i18n key.
 *
 * The backend returns a DRF ValidationError payload like:
 * { code: 'user_inactive' | 'subscription_not_found' | ..., detail: string }
 * This function maps the code to our translation namespace: `errors.<code>`.
 */
function normalizeBackendCodeToI18nKey(rawCode: string | undefined): string | null {
  if (!rawCode || rawCode.trim().length === 0) {
    return null;
  }

  // If it's already an i18n key, return as-is
  if (rawCode.startsWith('errors.')) {
    return rawCode;
  }

  // Take last enum segment if provided like: Namespace.CODE_NAME
  const lastSegment = rawCode.includes('.') ? rawCode.split('.').pop()! : rawCode;

  // Convert to snake_case lower
  const normalized = lastSegment
    .replace(/[^A-Za-z0-9]+/g, '_')
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .toLowerCase();

  return `errors.${normalized}`;
}

// Generic extractor: maps structured backend error payloads to i18n keys
// Expected DRF payload shape: { code?: string; detail?: string } but works with others too
export function extractErrorKey(error: any): string | null {
  if (!(error instanceof HttpErrorResponse)) return null;

  const payload = error.error as any;
  const code = payload?.code as string | undefined;
  const key = normalizeBackendCodeToI18nKey(code);
  return key;
}

export function convertToFormData(data: any): FormData {
  const formData = new FormData();

  for (const key in data) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
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
    // Prefer structured backend codes that we can translate on the UI
    const i18nKey = extractErrorKey(error);
    if (i18nKey) return i18nKey;

    // If backend sent a human-readable detail, show it as-is
    const detail = (error.error?.detail as string | undefined);
    if (typeof detail === 'string' && detail.trim().length > 0) {
      return detail;
    }

    if (error.error?.error) {
      return error.error?.error;
    }

    if (error.status === 400) {
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
