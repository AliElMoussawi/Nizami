import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditHistoryChatItemNameComponent } from './edit-history-chat-item-name.component';

describe('EditHistoryChatItemNameComponent', () => {
  let component: EditHistoryChatItemNameComponent;
  let fixture: ComponentFixture<EditHistoryChatItemNameComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditHistoryChatItemNameComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditHistoryChatItemNameComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
