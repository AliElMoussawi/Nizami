import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PersonalDetailsStep1Component } from './personal-details-step1.component';

describe('PersonalDetailsStepComponent', () => {
  let component: PersonalDetailsStep1Component;
  let fixture: ComponentFixture<PersonalDetailsStep1Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PersonalDetailsStep1Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PersonalDetailsStep1Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
