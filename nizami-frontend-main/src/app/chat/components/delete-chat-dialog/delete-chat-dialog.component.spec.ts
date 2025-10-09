import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteChatDialogComponent } from './delete-chat-dialog.component';

describe('DeleteChatDialogComponent', () => {
  let component: DeleteChatDialogComponent;
  let fixture: ComponentFixture<DeleteChatDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeleteChatDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeleteChatDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
