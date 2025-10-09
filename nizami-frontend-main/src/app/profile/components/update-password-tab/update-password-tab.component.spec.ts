import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdatePasswordTabComponent } from './update-password-tab.component';

describe('UpdatePasswordTabComponent', () => {
  let component: UpdatePasswordTabComponent;
  let fixture: ComponentFixture<UpdatePasswordTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdatePasswordTabComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdatePasswordTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
