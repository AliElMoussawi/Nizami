import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSideBarMobileHeaderComponent } from './chat-side-bar-mobile-header.component';

describe('ChatHeaderComponent', () => {
  let component: ChatSideBarMobileHeaderComponent;
  let fixture: ComponentFixture<ChatSideBarMobileHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSideBarMobileHeaderComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSideBarMobileHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
