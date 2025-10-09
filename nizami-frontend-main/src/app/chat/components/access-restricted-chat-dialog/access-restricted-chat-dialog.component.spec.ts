import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccessRestrictedChatDialogComponent } from './access-restricted-chat-dialog.component';

describe('DeleteChatDialogComponent', () => {
  let component: AccessRestrictedChatDialogComponent;
  let fixture: ComponentFixture<AccessRestrictedChatDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AccessRestrictedChatDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccessRestrictedChatDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
