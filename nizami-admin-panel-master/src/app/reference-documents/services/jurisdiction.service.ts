import {Injectable, signal} from '@angular/core';
import {environment} from '../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {EMPTY, map} from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class JurisdictionService {
  jurisdictions = signal<string[]>([]);
  isLoading = signal(true);
  isLoaded = signal(false);

  constructor(
    private http: HttpClient,
  ) {
  }

  get jurisdictionsCodes() {
    return this.jurisdictions() ?? [];
  }

  load() {
    if (this.isLoaded()) {
      return EMPTY;
    }
    return this.forceLoad();
  }

  forceLoad() {
    this.isLoading.set(true);
    return this.http.get<string[]>(
      environment.apiUrl + '/v1/admin/reference-documents/jurisdictions'
    ).pipe(
      map((response) => {
        this.isLoaded.set(true);
        this.jurisdictions.set(response);
        this.isLoading.set(false);
      }),
    );
  }
}
