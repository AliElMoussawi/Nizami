import {Component, forwardRef, HostListener, input, signal} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {NgIf} from '@angular/common';
import {FileSizePipe} from '../../../common/pipes/file-size.pipe';

@Component({
  selector: 'app-file-drag-zone',
  imports: [
    NgIf,
    FileSizePipe,
  ],
  templateUrl: './file-drag-zone.component.html',
  styleUrl: './file-drag-zone.component.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => FileDragZoneComponent),
      multi: true
    }
  ],
})
export class FileDragZoneComponent implements ControlValueAccessor {
  droppedFile: string | ArrayBuffer | null = null;
  file: File | null = null;
  label = input<string>();

  onChange: (value: any) => void = () => {
  };
  onTouched: () => void = () => {
  };

  // Prevent default behavior when dragging over
  @HostListener('dragover', ['$event'])
  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  // Handle file drop
  @HostListener('drop', ['$event'])
  onDrop(event: DragEvent) {
    event.preventDefault();

    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];

      // if (file.type.startsWith('image/')) {
      this.handleFile(file);
      // }
    }
  }

  // Implements ControlValueAccessor
  writeValue(value: any): void {
    this.droppedFile = value;
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  browse(file: HTMLInputElement) {
    file.click();
  }

  fileSelected(event: Event) {
    const fileInput = event.target as HTMLInputElement;
    if (fileInput.files && fileInput.files.length > 0) {
      const file = fileInput.files[0];
      this.handleFile(file);
    }
  }

  remove(fileInput: HTMLInputElement) {
    this.droppedFile = null;
    fileInput.files = null;
    fileInput.value = '';
    this.file = null;
    this.onChange(null);
    this.onTouched();
  }

  // Shared method to handle file processing
  private handleFile(file: File) {
    if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || file.name.endsWith('.docx')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.droppedFile = e.target?.result ?? null;
        this.file = file;
        this.onChange(this.file); // Notify Angular Form Control
        this.onTouched();
      };
      reader.readAsDataURL(file);
    }
  }
}
