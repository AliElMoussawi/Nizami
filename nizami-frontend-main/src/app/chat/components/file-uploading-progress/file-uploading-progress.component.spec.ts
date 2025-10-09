import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileUploadingProgressComponent } from './file-uploading-progress.component';

describe('FileUploadingProgressComponent', () => {
  let component: FileUploadingProgressComponent;
  let fixture: ComponentFixture<FileUploadingProgressComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FileUploadingProgressComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FileUploadingProgressComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
