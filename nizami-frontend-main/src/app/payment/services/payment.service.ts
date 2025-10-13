import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { Plan } from '../models/plan.model';
import { PaginatedResponse } from '../models/paginated-response.model';

@Injectable({
  providedIn: 'root'
})
export class PaymentService {
  private baseUrl = `${environment.apiUrl}/v1`;

  constructor(private http: HttpClient) {}

  getPlan(planId: string): Observable<Plan> {
    return this.http.get<Plan>(`${this.baseUrl}/plans/${planId}`);
  }

  listAvailableUpgradePlans(): Observable<Plan[]> {
    const url = `${this.baseUrl}/plans/available-for-upgrade`;
  
    return this.http.get<PaginatedResponse<Plan>>(url).pipe(
      map(response => {
        console.log('[PaymentService] listAvailableUpgradePlans response:', response);
        
        // Handle if response is null or undefined
        if (!response) {
          console.warn('[PaymentService] Empty response');
          return [];
        }

        // Handle if response.data doesn't exist
        if (!response.data) {
          console.warn('[PaymentService] No data property in response:', response);
          return [];
        }

        // Handle if response.data is not an array
        if (!Array.isArray(response.data)) {
          console.error('[PaymentService] response.data is not an array:', typeof response.data, response.data);
          return [];
        }

        console.log('[PaymentService] Returning plans:', response.data.length);
        return response.data;
      }),
      catchError(error => {
        console.error('[PaymentService] Error fetching plans:', error);
        return of([]);
      })
    );
  }

  syncPaymentStatus(paymentId: string): Observable<any> {
    const url = `${this.baseUrl}/payment/${paymentId}/sync/`;
    
    return this.http.post<any>(url, {}).pipe(
      map(response => {
        console.log('[PaymentService] syncPaymentStatus response:', response);
        return response;
      }),
      catchError(error => {
        console.error('[PaymentService] Error syncing payment:', error);
        throw error;
      })
    );
  }
}

