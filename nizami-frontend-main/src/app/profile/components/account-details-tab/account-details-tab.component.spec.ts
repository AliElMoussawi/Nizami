import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccountDetailsTabComponent } from './account-details-tab.component';

describe('AccountDetailsTabComponent', () => {
  let component: AccountDetailsTabComponent;
  let fixture: ComponentFixture<AccountDetailsTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AccountDetailsTabComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccountDetailsTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
