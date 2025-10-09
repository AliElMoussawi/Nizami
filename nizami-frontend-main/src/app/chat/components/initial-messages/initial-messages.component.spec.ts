import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InitialMessagesComponent } from './initial-messages.component';

describe('InitialMessagesComponent', () => {
  let component: InitialMessagesComponent;
  let fixture: ComponentFixture<InitialMessagesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InitialMessagesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InitialMessagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
