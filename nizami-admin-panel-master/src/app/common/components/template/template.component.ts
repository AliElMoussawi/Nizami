import { Component } from '@angular/core';
import {HeaderComponent} from '../header/header.component';
import {SidebarComponent} from '../sidebar/sidebar.component';

@Component({
  selector: 'app-template',
  imports: [
    HeaderComponent,
    SidebarComponent
  ],
  templateUrl: './template.component.html',
  styleUrl: './template.component.scss'
})
export class TemplateComponent {

}
