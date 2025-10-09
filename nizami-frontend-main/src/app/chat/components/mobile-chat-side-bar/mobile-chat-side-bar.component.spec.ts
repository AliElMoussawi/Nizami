import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MobileChatSideBarComponent } from './mobile-chat-side-bar.component';

describe('MobileChatSideBarComponent', () => {
  let component: MobileChatSideBarComponent;
  let fixture: ComponentFixture<MobileChatSideBarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MobileChatSideBarComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MobileChatSideBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
