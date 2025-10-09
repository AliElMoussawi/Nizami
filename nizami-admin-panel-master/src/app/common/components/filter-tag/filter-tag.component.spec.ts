import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FilterTagComponent } from './filter-tag.component';

describe('FilterTagComponent', () => {
  let component: FilterTagComponent;
  let fixture: ComponentFixture<FilterTagComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterTagComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FilterTagComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
