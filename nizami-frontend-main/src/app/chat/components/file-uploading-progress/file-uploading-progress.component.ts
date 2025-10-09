import {Component, input, Input, output, signal} from '@angular/core';
import {FileModel} from '../../models/message.model';
import {NgIcon} from '@ng-icons/core';
import {NgClass} from '@angular/common';
import {FileSizePipe} from '../../../common/pipes/file-size.pipe';

@Component({
  selector: 'app-file-uploading-progress',
  imports: [
    NgClass,
    FileSizePipe
  ],
  templateUrl: './file-uploading-progress.component.html',
  styleUrl: './file-uploading-progress.component.scss'
})
export class FileUploadingProgressComponent {
  file = input.required<FileModel>();
  progress = input.required<number>();
  error = input.required<any>();
  onRemove = output();
  onTryAgain = output();

  showDeleteButton = signal(false);
}
