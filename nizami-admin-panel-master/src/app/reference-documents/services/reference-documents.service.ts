import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {DataTableResponse} from '../../common/models/data-table.response';
import {ReferenceDocumentModel} from '../models/reference-document.model';
import {AuthService} from '../../auth/services/auth.service';
import {catchError, EMPTY, map} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {extractErrorFromResponse} from '../../common/utils';

@Injectable({
  providedIn: 'root'
})
export class ReferenceDocumentsService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private toastr: ToastrService,
  ) {
  }

  getDocuments(dataTablesParameters: any) {
    return this.http.post<DataTableResponse<any>>(
      environment.apiUrl + '/v1/admin/reference-documents/get',
      dataTablesParameters,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  createDocument(data: any) {
    return this.http.post<any>(
      environment.apiUrl + '/v1/admin/reference-documents/',
      data,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  loadDocument(id: any) {
    return this.http.get<ReferenceDocumentModel>(
      environment.apiUrl + '/v1/admin/reference-documents/' + id + '/get',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  updateDocument(id: any, value: any) {
    return this.http.put<any>(
      environment.apiUrl + '/v1/admin/reference-documents/' + id + '/edit',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  deleteDocument(id: any) {
    return this.http.delete<any>(
      environment.apiUrl + '/v1/admin/reference-documents/' + id,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  downloadDocument(ref_doc: ReferenceDocumentModel) {
    return this.http.get(
      environment.apiUrl + '/v1/admin/reference-documents/' + ref_doc.id + '/get-file',
      {
        responseType: 'blob',
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    )
      .pipe(
        map(
          (blob) => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = ref_doc.file_name;
            link.click();

            return blob;
          },
        ),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed downloading the document");

          return EMPTY;
        }),
      );
  }
}
