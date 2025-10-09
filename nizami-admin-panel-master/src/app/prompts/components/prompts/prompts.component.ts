import {AfterViewInit, Component, OnDestroy, OnInit, signal} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {DataTablesModule} from "angular-datatables";
import {FormsModule} from '@angular/forms';
import {DatePipe} from '@angular/common';
import {ToastrService} from 'ngx-toastr';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {PromptsService} from '../../services/prompts.service';
import {PromptModel} from '../../models/prompt.model';
import {FileSizePipe} from '../../../common/pipes/file-size.pipe';
import {catchError, EMPTY, finalize, take} from 'rxjs';
import {SpinnerComponent} from '../../../common/components/spinner/spinner.component';
import {EditPromptComponent} from '../edit-prompt/edit-prompt.component';
import {extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-prompts',
  imports: [
    TemplateComponent,
    DataTablesModule,
    FormsModule,
    SpinnerComponent,
    EditPromptComponent
  ],
  providers: [
    DatePipe,
    FileSizePipe,
  ],
  templateUrl: './prompts.component.html',
  styleUrl: './prompts.component.scss'
})
export class PromptsComponent implements OnInit, AfterViewInit, OnDestroy {
  prompts = signal<PromptModel[]>([]);
  isLoading = signal(true);

  constructor(
    private promptsService: PromptsService,
    private toastr: ToastrService,
  ) {
  }

  ngOnDestroy() {
  }

  ngAfterViewInit() {
  }

  ngOnInit(): void {
    this.loadPrompts();
  }


  private loadPrompts() {
    this.isLoading.set(true);

    this.promptsService
      .getAll()
      .pipe(
        take(1),
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed to load prompts");

          return EMPTY;
        }),
        finalize(() => {
          this.isLoading.set(false);
        }),
      )
      .subscribe((prompts) => {
        this.prompts.set(prompts);
      });
  }
}
