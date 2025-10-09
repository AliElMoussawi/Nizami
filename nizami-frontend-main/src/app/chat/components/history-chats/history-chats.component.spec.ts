import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoryChatsComponent } from './history-chats.component';

describe('HistoryChatsComponent', () => {
  let component: HistoryChatsComponent;
  let fixture: ComponentFixture<HistoryChatsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HistoryChatsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryChatsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
