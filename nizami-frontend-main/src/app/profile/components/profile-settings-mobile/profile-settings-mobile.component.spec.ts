import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileSettingsMobileComponent } from './profile-settings-mobile.component';

describe('ProfileSettingsDialogComponent', () => {
  let component: ProfileSettingsMobileComponent;
  let fixture: ComponentFixture<ProfileSettingsMobileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfileSettingsMobileComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfileSettingsMobileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
