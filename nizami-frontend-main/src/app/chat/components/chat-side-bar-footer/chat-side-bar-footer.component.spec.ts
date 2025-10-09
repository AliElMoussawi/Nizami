import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSideBarFooterComponent } from './chat-side-bar-footer.component';

describe('ChatSideBarFooterComponent', () => {
  let component: ChatSideBarFooterComponent;
  let fixture: ComponentFixture<ChatSideBarFooterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSideBarFooterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSideBarFooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
