import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {AuthService} from '../../auth/services/auth.service';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {Payment, PaymentStatistics, DataTableResponse} from '../types/payment.types';

@Injectable({
  providedIn: 'root'
})
export class PaymentsService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {
  }

  getPayments(dataTablesParameters: any): Observable<DataTableResponse<Payment>> {
    return this.http.post<DataTableResponse<Payment>>(
      environment.apiUrl + '/v1/admin/payments/get',
      dataTablesParameters,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  getPaymentStatistics(days: number = 30): Observable<PaymentStatistics> {
    return this.http.get<PaymentStatistics>(
      environment.apiUrl + `/v1/admin/payments/statistics?days=${days}`,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }


  getPaymentDetails(paymentId: string): Observable<Payment> {
    return this.http.get<Payment>(
      environment.apiUrl + `/v1/admin/payments/${paymentId}/details`,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  getTotalPaymentsCount(): Observable<number> {
    return this.http.get<{total_count: number}>(
      environment.apiUrl + '/v1/admin/payments/total-count',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    ).pipe(
      map(response => response.total_count || 0)
    );
  }

}
