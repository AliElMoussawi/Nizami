import {Component, Input, output} from '@angular/core';

@Component({
  selector: 'app-profile-image-input',
  imports: [],
  templateUrl: './profile-image-input.component.html',
  styleUrl: './profile-image-input.component.scss'
})
export class ProfileImageInputComponent {
  imagePreview: string | null = null;
  selectedFile: File | null = null;

  onSelectFile = output<File | null>();

  @Input()
  set initial(file: any) {
    this.selectedFile = file;

    if (this.selectedFile) {
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };

      reader.readAsDataURL(file);
    }
  }

  @Input()
  set initialUrl(url: string | undefined | null) {
    if(url) {
      this.imagePreview = url;
    }
  }

  selectFile($event: Event) {
    const file = ($event.target as HTMLInputElement).files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        return;
      }

      this.selectedFile = file;

      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };

      reader.readAsDataURL(file);

      this.onSelectFile.emit(this.selectedFile);
    }
  }

  clearFile(file: HTMLInputElement) {
    file.files = null;
    this.selectedFile = null;
    this.imagePreview = null;

    this.onSelectFile.emit(this.selectedFile);
  }
}
