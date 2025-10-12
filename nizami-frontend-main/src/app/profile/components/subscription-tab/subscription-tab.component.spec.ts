import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionTabComponent } from './subscription-tab.component';

describe('SubscriptionTabComponent', () => {
  let component: SubscriptionTabComponent;
  let fixture: ComponentFixture<SubscriptionTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SubscriptionTabComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
