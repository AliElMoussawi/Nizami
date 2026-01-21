import {Routes} from '@angular/router';
import {LoginComponent} from './auth/components/login/login.component';
import {GuestGuard} from './auth/guards/guest.guard';
import {ForgotPasswordComponent} from './auth/components/forgot-password/forgot-password.component';
import {ResetPasswordComponent} from './auth/components/reset-password/reset-password.component';
import {AuthenticatedGuard} from './auth/guards/authenticated.guard';
import {DashboardComponent} from './dashboard/components/dashboard/dashboard.component';
import {UsersComponent} from './users/components/users/users.component';
import {ReferenceDocumentsComponent} from './reference-documents/components/reference-documents/reference-documents.component';
import {CreateUserComponent} from './users/components/create-user/create-user.component';
import {EditUserComponent} from './users/components/edit-user/edit-user.component';
import {ReferenceDocumentsService} from './reference-documents/services/reference-documents.service';
import {
  CreateReferenceDocumentComponent
} from './reference-documents/components/create-reference-document/create-reference-document.component';
import {
  EditReferenceDocumentComponent
} from './reference-documents/components/edit-reference-document/edit-reference-document.component';
import {PromptsComponent} from './prompts/components/prompts/prompts.component';
import {PlansComponent} from './plan/components/plans/plans.component';
import {CreatePlanComponent} from './plan/components/create-plan/create-plan.component';
import {EditPlanComponent} from './plan/components/edit-plan/edit-plan.component';
import {SubscriptionsComponent} from './subscriptions/components/subscriptions/subscriptions.component';
import {CreateSubscriptionComponent} from './subscriptions/components/create-subscription/create-subscription.component';
import {EditSubscriptionComponent} from './subscriptions/components/edit-subscription/edit-subscription.component';
import {PaymentsComponent} from './payments/components/payments/payments.component';
import {UserRequestsComponent} from './user-requests/components/user-requests/user-requests.component';

export const routes: Routes = [
  {
    path: 'plans',
    children: [
      {
        path: 'create',
        component: CreatePlanComponent,
      },
      {
        path: ':uuid/edit',
        component: EditPlanComponent,
      },
      {
        path: '',
        component: PlansComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: 'login',
    component: LoginComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'reset-password',
    component: ResetPasswordComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthenticatedGuard],
  },
  {
    path: 'users',
    children: [
      {
        path: 'create',
        component: CreateUserComponent,
      },
      {
        path: ':id/edit',
        component: EditUserComponent,
      },
      {
        path: '',
        component: UsersComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: 'documents',
    children: [
      {
        path: 'create',
        component: CreateReferenceDocumentComponent,
      },
      {
        path: ':id/edit',
        component: EditReferenceDocumentComponent,
      },
      {
        path: '',
        component: ReferenceDocumentsComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: 'prompts',
    children: [
      {
        path: '',
        component: PromptsComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: 'subscriptions',
    children: [
      {
        path: 'create',
        component: CreateSubscriptionComponent,
      },
      {
        path: ':uuid/edit',
        component: EditSubscriptionComponent,
      },
      {
        path: '',
        component: SubscriptionsComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: 'payments',
    children: [
      {
        path: '',
        component: PaymentsComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: 'user-requests',
    children: [
      {
        path: '',
        component: UserRequestsComponent,
      },
    ],
    canActivateChild: [AuthenticatedGuard],
  },
  {
    path: '**',
    redirectTo: 'login',
  },
];
