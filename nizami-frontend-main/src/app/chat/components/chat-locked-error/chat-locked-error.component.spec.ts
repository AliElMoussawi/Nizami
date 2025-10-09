import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatLockedErrorComponent } from './chat-locked-error.component';

describe('ErrorMessageComponent', () => {
  let component: ChatLockedErrorComponent;
  let fixture: ComponentFixture<ChatLockedErrorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatLockedErrorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatLockedErrorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
