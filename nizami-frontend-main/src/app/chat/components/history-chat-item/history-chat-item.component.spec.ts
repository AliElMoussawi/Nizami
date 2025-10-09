import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoryChatItemComponent } from './history-chat-item.component';

describe('HistoryChatItemComponent', () => {
  let component: HistoryChatItemComponent;
  let fixture: ComponentFixture<HistoryChatItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HistoryChatItemComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryChatItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
