import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PasswordValidationErrorsComponent } from './password-validation-errors.component';

describe('PasswordValidationErrorsComponent', () => {
  let component: PasswordValidationErrorsComponent;
  let fixture: ComponentFixture<PasswordValidationErrorsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PasswordValidationErrorsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PasswordValidationErrorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
