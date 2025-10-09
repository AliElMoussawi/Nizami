import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JurisdictionListComponent } from './jurisdiction-list.component';

describe('JurisdicationListComponent', () => {
  let component: JurisdictionListComponent;
  let fixture: ComponentFixture<JurisdictionListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JurisdictionListComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JurisdictionListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
