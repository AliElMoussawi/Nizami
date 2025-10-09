import {HttpErrorResponse} from '@angular/common/http';

export function convertToFormData(data: any): FormData {
  const formData = new FormData();

  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      if(data[key] instanceof Array) {
        data[key].forEach((item) => {formData.append(key, item);});
      } else if (data[key] instanceof File) {
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

    if(error.error?.detail) {
      return error.error?.detail;
    }

    if (error.status == 400) {
      return Object.values(error.error)[0] as string;
    }
  }

  return null;
}
