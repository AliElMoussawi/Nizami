import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSideBarMobileFooterComponent } from './chat-side-bar-mobile-footer.component';

describe('ChatSideBarMobileFooterComponent', () => {
  let component: ChatSideBarMobileFooterComponent;
  let fixture: ComponentFixture<ChatSideBarMobileFooterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSideBarMobileFooterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSideBarMobileFooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
