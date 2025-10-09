import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ControlErrorsComponent } from './control-errors.component';

describe('ErrorComponent', () => {
  let component: ControlErrorsComponent;
  let fixture: ComponentFixture<ControlErrorsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ControlErrorsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ControlErrorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
