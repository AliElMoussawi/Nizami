import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserMessageFileComponent } from './user-message-file.component';

describe('UserMessageFileComponent', () => {
  let component: UserMessageFileComponent;
  let fixture: ComponentFixture<UserMessageFileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserMessageFileComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserMessageFileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
