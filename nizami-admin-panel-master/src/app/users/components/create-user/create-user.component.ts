import {Component, signal, viewChild} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {UsersService} from '../../services/users.service';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {Router, RouterLink} from '@angular/router';
import {UserFormComponent} from '../user-form/user-form.component';
import {convertToFormData, extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-create-user',
  imports: [
    ReactiveFormsModule,
    TemplateComponent,
    RouterLink,
    UserFormComponent
  ],
  templateUrl: './create-user.component.html',
  styleUrl: './create-user.component.scss'
})
export class CreateUserComponent {
  isCreating = signal<boolean>(false);
  userForm = viewChild(UserFormComponent);

  constructor(
    private user: UsersService,
    private toastr: ToastrService,
    private router: Router,
  ) {
  }

  submit(value: any, reset: boolean = false) {
    this.isCreating.set(true);

    this.user
      .createUser(convertToFormData(value))
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed creating user");

          return EMPTY;
        }),
        finalize(() => {
          this.isCreating.set(false);
        })
      )
      .subscribe(() => {
        this.toastr.success('User successfully created');

        if (reset) {
          // this.userForm()?.form?.reset();
        } else {
          this.router.navigateByUrl('/users');
        }
      });
  }
}
