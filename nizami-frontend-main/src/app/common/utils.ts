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


const URDU_SPECIFIC_CHARS = new Set('ٹڈڑںھہےیګکپچژ');
const FRENCH_ACCENT_RE = /[àâçéèêëîïôûùüÿœæ]/;
const FRENCH_MARKERS = [
  ' le ', ' la ', ' les ', ' de ', ' des ', ' du ', ' et ', ' est ',
  ' que ', ' pour ', ' avec ', ' dans ', ' sur ', ' pas ', ' une ', ' un ',
];

export function detectLanguage(text: string): string {
  let devanagariCount = 0;
  let arabicScriptCount = 0;
  let latinCount = 0;
  let urduSpecificCount = 0;

  for (const char of text) {
    if (char >= '\u0900' && char <= '\u097F') {
      devanagariCount++;
    } else if (char >= '\u0600' && char <= '\u06FF') {
      arabicScriptCount++;
      if (URDU_SPECIFIC_CHARS.has(char)) {
        urduSpecificCount++;
      }
    } else if ((char >= 'A' && char <= 'Z') || (char >= 'a' && char <= 'z')) {
      latinCount++;
    }
  }

  if (devanagariCount > 0) {
    return 'hi';
  }

  if (arabicScriptCount > 0) {
    return urduSpecificCount > 0 ? 'ur' : 'ar';
  }

  if (latinCount > 0) {
    const lower = ` ${text.toLowerCase()} `;
    if (FRENCH_ACCENT_RE.test(lower) || FRENCH_MARKERS.some(m => lower.includes(m))) {
      return 'fr';
    }
    return 'en';
  }

  return 'ar';
}
