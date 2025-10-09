import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratingResponseMessageComponent } from './generating-response-message.component';

describe('GeneratingResponseMessageComponent', () => {
  let component: GeneratingResponseMessageComponent;
  let fixture: ComponentFixture<GeneratingResponseMessageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneratingResponseMessageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratingResponseMessageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
