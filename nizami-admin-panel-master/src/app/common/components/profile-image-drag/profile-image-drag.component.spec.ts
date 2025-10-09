import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileImageDragComponent } from './profile-image-drag.component';

describe('ProfileImageInputComponent', () => {
  let component: ProfileImageDragComponent;
  let fixture: ComponentFixture<ProfileImageDragComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfileImageDragComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfileImageDragComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
