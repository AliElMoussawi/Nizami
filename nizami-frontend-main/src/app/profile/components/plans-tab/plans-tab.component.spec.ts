import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PlansTabComponent } from './plans-tab.component';
import { PaymentService } from '../../../payment/services/payment.service';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { Plan } from '../../../payment/models/plan.model';

describe('PlansTabComponent', () => {
  let component: PlansTabComponent;
  let fixture: ComponentFixture<PlansTabComponent>;
  let paymentServiceSpy: jasmine.SpyObj<PaymentService>;
  let routerSpy: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    paymentServiceSpy = jasmine.createSpyObj('PaymentService', ['listAvailableUpgradePlans']);
    routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [PlansTabComponent],
      providers: [
        { provide: PaymentService, useValue: paymentServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(PlansTabComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load plans successfully', () => {
    const mockPlans: Plan[] = [
      { uuid: '1', name: 'Basic', price_cents: 1000, currency: 'USD' } as Plan
    ];
    paymentServiceSpy.listAvailableUpgradePlans.and.returnValue(of(mockPlans));

    component.ngOnInit();

    expect(paymentServiceSpy.listAvailableUpgradePlans).toHaveBeenCalled();
    expect(component.plans).toEqual(mockPlans);
    expect(component.loading).toBeFalse();
    expect(component.error).toBeNull();
  });

  it('should handle error when loading plans fails', () => {
    paymentServiceSpy.listAvailableUpgradePlans.and.returnValue(throwError(() => new Error('Network error')));

    component.ngOnInit();

    expect(paymentServiceSpy.listAvailableUpgradePlans).toHaveBeenCalled();
    expect(component.error).toContain('Failed to load plans');
    expect(component.loading).toBeFalse();
    expect(component.plans.length).toBe(0);
  });

  it('should navigate when selecting a plan', () => {
    const plan = { uuid: 'abc123' } as Plan;
    component.selectPlan(plan);
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/payment', 'abc123']);
  });

  it('should format price correctly', () => {
    expect(component.formatPrice(2500, 'USD')).toBe('25.00 USD');
  });

  it('should return correct interval text', () => {
    expect(component.getIntervalText('month', 1)).toBe('/ month');
    expect(component.getIntervalText('month', 3)).toBe('/ 3 months');
  });
});
