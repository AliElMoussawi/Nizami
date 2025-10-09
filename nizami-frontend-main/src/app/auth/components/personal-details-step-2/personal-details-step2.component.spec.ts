import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PersonalDetailsStep2Component } from './personal-details-step2.component';

describe('PersonalDetailsStepComponent', () => {
  let component: PersonalDetailsStep2Component;
  let fixture: ComponentFixture<PersonalDetailsStep2Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PersonalDetailsStep2Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PersonalDetailsStep2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
