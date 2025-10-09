import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileImageInputComponent } from './profile-image-input.component';

describe('ProfileImageInputComponent', () => {
  let component: ProfileImageInputComponent;
  let fixture: ComponentFixture<ProfileImageInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfileImageInputComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfileImageInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
