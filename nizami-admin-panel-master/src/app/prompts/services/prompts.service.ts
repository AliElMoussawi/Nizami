import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {PromptModel} from '../models/prompt.model';
import {AuthService} from '../../auth/services/auth.service';
import {ToastrService} from 'ngx-toastr';

@Injectable({
  providedIn: 'root'
})
export class PromptsService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private toastr: ToastrService,
  ) {
  }

  getAll() {
    return this.http.post<PromptModel[]>(
      environment.apiUrl + '/v1/admin/prompts/get',
      {

      },
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }


  updatePrompt(id: any, value: any) {
    return this.http.put<PromptModel>(
      environment.apiUrl + '/v1/admin/prompts/' + id + '/edit',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}
