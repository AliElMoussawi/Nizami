import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSideBarHeaderComponent } from './chat-side-bar-header.component';

describe('ChatHeaderComponent', () => {
  let component: ChatSideBarHeaderComponent;
  let fixture: ComponentFixture<ChatSideBarHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSideBarHeaderComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSideBarHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
