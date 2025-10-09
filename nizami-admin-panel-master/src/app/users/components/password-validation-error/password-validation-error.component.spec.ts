import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PasswordValidationErrorComponent } from './password-validation-error.component';

describe('PasswordValidationErrorComponent', () => {
  let component: PasswordValidationErrorComponent;
  let fixture: ComponentFixture<PasswordValidationErrorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PasswordValidationErrorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PasswordValidationErrorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
