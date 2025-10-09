import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReferenceDocumentsComponent } from './reference-documents.component';

describe('DocumentsComponent', () => {
  let component: ReferenceDocumentsComponent;
  let fixture: ComponentFixture<ReferenceDocumentsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReferenceDocumentsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReferenceDocumentsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
