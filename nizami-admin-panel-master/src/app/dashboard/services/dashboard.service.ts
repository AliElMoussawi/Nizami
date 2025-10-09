import { Injectable } from '@angular/core';
import {ReferenceDocumentModel} from '../../reference-documents/models/reference-document.model';
import {environment} from '../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {AuthService} from '../../auth/services/auth.service';
import {DashboardCardModel} from '../models/dashboard-card.model';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) { }

  loadCards() {
    return this.http.get<DashboardCardModel[]>(
      environment.apiUrl + '/v1/admin/dashboard/cards',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}
