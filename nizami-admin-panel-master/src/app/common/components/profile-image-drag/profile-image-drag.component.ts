import {Component, forwardRef, HostListener} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {NgIf} from '@angular/common';
import {FileSizePipe} from '../../pipes/file-size.pipe';

@Component({
  selector: 'app-profile-image-drag',
  imports: [
    NgIf,
    FileSizePipe
  ],
  templateUrl: './profile-image-drag.component.html',
  styleUrl: './profile-image-drag.component.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => ProfileImageDragComponent),
      multi: true
    }
  ],
})
export class ProfileImageDragComponent implements ControlValueAccessor {
  droppedImage: string | ArrayBuffer | null = null;
  file: File | null = null;

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

      if (file.type.startsWith('image/')) {
        this.handleFile(file);
      }
    }
  }

  // Implements ControlValueAccessor
  writeValue(value: any): void {
    this.droppedImage = value;
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
    this.droppedImage = null;
    fileInput.files = null;
    fileInput.value = '';
    this.file = null;
    this.onChange(null);
    this.onTouched();
  }

  // Shared method to handle file processing
  private handleFile(file: File) {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.droppedImage = e.target?.result ?? null;
        this.file = file;
        this.onChange(this.file); // Notify Angular Form Control
        this.onTouched();
      };
      reader.readAsDataURL(file);
    }
  }
}
