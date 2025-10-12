import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpgradePlansDialogComponent } from './upgrade-plans-dialog.component';

describe('UpgradePlansDialogComponent', () => {
  let component: UpgradePlansDialogComponent;
  let fixture: ComponentFixture<UpgradePlansDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpgradePlansDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpgradePlansDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
