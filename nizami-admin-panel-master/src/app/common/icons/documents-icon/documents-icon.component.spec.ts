import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentsIconComponent } from './documents-icon.component';

describe('DocumentsImageComponent', () => {
  let component: DocumentsIconComponent;
  let fixture: ComponentFixture<DocumentsIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DocumentsIconComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DocumentsIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
