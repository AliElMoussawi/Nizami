import {Component, input} from '@angular/core';
import {FileModel} from '../../models/message.model';
import {NgIcon} from '@ng-icons/core';
import {FileSizePipe} from '../../../common/pipes/file-size.pipe';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-user-message-file',
  imports: [
    FileSizePipe,
    NgClass
  ],
  templateUrl: './user-message-file.component.html',
  styleUrl: './user-message-file.component.scss'
})
export class UserMessageFileComponent {
  file = input.required<FileModel>();
  selectable = input(false);
  isUserMessage = input(true);
}
