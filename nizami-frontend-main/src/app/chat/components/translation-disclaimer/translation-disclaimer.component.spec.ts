import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TranslationDisclaimerComponent } from './translation-disclaimer.component';

describe('TranslationDisclaimerComponent', () => {
  let component: TranslationDisclaimerComponent;
  let fixture: ComponentFixture<TranslationDisclaimerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TranslationDisclaimerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TranslationDisclaimerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
