import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateReferenceDocumentComponent } from './create-reference-document.component';

describe('CreateUserComponent', () => {
  let component: CreateReferenceDocumentComponent;
  let fixture: ComponentFixture<CreateReferenceDocumentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateReferenceDocumentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateReferenceDocumentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
