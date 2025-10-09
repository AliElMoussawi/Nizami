import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileDragZoneComponent } from './file-drag-zone.component';

describe('ProfileImageInputComponent', () => {
  let component: FileDragZoneComponent;
  let fixture: ComponentFixture<FileDragZoneComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FileDragZoneComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FileDragZoneComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
