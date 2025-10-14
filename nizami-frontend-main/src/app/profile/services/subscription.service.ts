import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { UserSubscription } from '../models/subscription.model';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {
  private apiUrl = `${environment.apiUrl}/v1/subscriptions`;

  constructor(private http: HttpClient) {}

  getActiveSubscription(): Observable<UserSubscription> {
    return this.http.get<UserSubscription>(`${this.apiUrl}/active/`);
  }

  getLatestSubscription(): Observable<UserSubscription> {
    return this.http.get<UserSubscription>(`${this.apiUrl}/latest/`);
  }

  getSubscriptionHistory(): Observable<any> {
    return this.http.get(`${this.apiUrl}/history/`);
  }

  cancelSubscription(): Observable<any> {
    return this.http.post(`${this.apiUrl}/deactivate/`, {});
  }
}

