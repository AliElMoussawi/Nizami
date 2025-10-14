import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-payment-callback',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslatePipe],
  templateUrl: './payment-callback.component.html',
  styleUrls: ['./payment-callback.component.scss']
})
export class PaymentCallbackComponent implements OnInit {
  status: string | null = null;
  message: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.status = params['status'] || null;
      this.message = params['message'] || null;
      
      if (this.status === 'paid') {
        const paymentId = params['id'];
        this.router.navigate(['/payment/success'], { 
          queryParams: { paymentId } 
        });
      } else {
        setTimeout(() => {
          this.router.navigate(['/chat']);
        }, 3000);
      }
    });
  }
}

