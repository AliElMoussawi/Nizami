import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TabsButtonComponent } from './tabs-button.component';

describe('TabsButtonComponent', () => {
  let component: TabsButtonComponent;
  let fixture: ComponentFixture<TabsButtonComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TabsButtonComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TabsButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
