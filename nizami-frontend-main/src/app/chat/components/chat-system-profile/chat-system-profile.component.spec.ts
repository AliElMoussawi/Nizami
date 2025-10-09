import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSystemProfileComponent } from './chat-system-profile.component';

describe('ChatSystemProfileComponent', () => {
  let component: ChatSystemProfileComponent;
  let fixture: ComponentFixture<ChatSystemProfileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSystemProfileComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSystemProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
