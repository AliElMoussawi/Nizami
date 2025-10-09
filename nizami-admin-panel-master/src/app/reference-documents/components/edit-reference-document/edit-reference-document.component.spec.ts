import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditReferenceDocumentComponent } from './edit-reference-document.component';

describe('CreateUserComponent', () => {
  let component: EditReferenceDocumentComponent;
  let fixture: ComponentFixture<EditReferenceDocumentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditReferenceDocumentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditReferenceDocumentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
