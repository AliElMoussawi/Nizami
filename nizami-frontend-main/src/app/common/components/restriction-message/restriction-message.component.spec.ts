import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RestrictionMessageComponent } from './restriction-message.component';

describe('RestrictionMessageComponent', () => {
  let component: RestrictionMessageComponent;
  let fixture: ComponentFixture<RestrictionMessageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestrictionMessageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RestrictionMessageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
