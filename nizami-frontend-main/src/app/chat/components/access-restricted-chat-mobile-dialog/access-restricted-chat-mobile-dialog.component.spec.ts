import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccessRestrictedChatMobileDialogComponent } from './access-restricted-chat-mobile-dialog.component';

describe('DeleteChatDialogComponent', () => {
  let component: AccessRestrictedChatMobileDialogComponent;
  let fixture: ComponentFixture<AccessRestrictedChatMobileDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AccessRestrictedChatMobileDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccessRestrictedChatMobileDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
