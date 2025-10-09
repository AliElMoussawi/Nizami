import {Component, signal} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {UsersService} from '../../services/users.service';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {ActivatedRoute, Router, RouterLink} from '@angular/router';
import {UserModel} from '../../../common/models/user.model';
import {UserFormComponent} from '../user-form/user-form.component';
import {SpinnerComponent} from '../../../common/components/spinner/spinner.component';
import {convertToFormData, extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-create-userService',
  imports: [
    ReactiveFormsModule,
    TemplateComponent,
    RouterLink,
    UserFormComponent,
    SpinnerComponent
  ],
  templateUrl: './edit-user.component.html',
  styleUrl: './edit-user.component.scss'
})
export class EditUserComponent {
  isLoading = signal<boolean>(true);
  isUpdating = signal<boolean>(false);
  user = signal<UserModel | null>(null);

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private userService: UsersService,
    private toastr: ToastrService,
  ) {
    let id = this.route.snapshot.params['id'];

    if (!id) {
      this.router.navigateByUrl('/users');
    }

    this.loadUser(id);
  }

  submit(value: any) {
    this.isUpdating.set(true);

    let formData = value;

    if (typeof formData.profile_image == 'string' || !formData.profile_image) {
      delete formData['profile_image'];
    }

    this.userService
      .updateUser(this.user()!.id, convertToFormData(value))
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed updating user");

          return EMPTY;
        }),
        finalize(() => {
          this.isUpdating.set(false);
        })
      )
      .subscribe(() => {
        this.toastr.success('User successfully updated');
      });
  }

  private loadUser(id: any) {
    this.userService
      .loadUser(id)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed loading the user");

          return EMPTY;
        }),
      )
      .subscribe((user) => {
        this.user.set(user);

        this.isLoading.set(false);
      });
  }

  redirect() {
    this.router.navigateByUrl('/users');
  }
}
