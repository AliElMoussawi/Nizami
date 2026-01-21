import {HttpClient, HttpHeaders, HttpRequest} from '@angular/common/http';
import {FileModel, MessageModel} from '../models/message.model';
import {Injectable} from '@angular/core';
import {environment} from '../../../environments/environment';
import {ChatModel} from '../models/chat.model';
import {AuthService} from '../../auth/services/auth.service';
import {IdPaginationModel, PaginationModel} from '../../common/models/pagination.model';
import {catchError, EMPTY, map, timeout} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {extractErrorFromResponse} from '../../common/utils';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslateService} from '@ngx-translate/core';

@Injectable({
  providedIn: 'root',
})
export class MessagesService {
  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private toastr: ToastrService,
    private translate: TranslateService,
  ) {
  }

  createChat(text: string) {
    return this.http.post<ChatModel>(
      environment.apiUrl + '/v1/chats/',
      {
        first_text_message: text,
      },
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  sendMessage(message: MessageModel) {
    return this.http.post<MessageModel>(
      environment.apiUrl + '/v1/chats/messages/create', message,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    ).pipe(timeout(360000));
  }

  getChats(search: any, page: any, per_page = 25) {
    return this.http.get<PaginationModel<ChatModel>>(
      environment.apiUrl + '/v1/chats/get',
      {
        params: {page, per_page, search: search || ''},
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  loadMessages(chat_id: any, last_id: number | null = null, per_page = 50) {
    const params: { [param: string]: string | number | boolean } = {
      per_page,
    };

    if (last_id) {
      params['last_id'] = last_id!;
    }

    return this.http.get<IdPaginationModel<MessageModel>>(
      environment.apiUrl + '/v1/chats/' + chat_id + '/messages',
      {
        params: params,
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  deleteChat(chat: ChatModel) {
    return this.http.delete<void>(
      environment.apiUrl + '/v1/chats/' + chat.id + '/delete',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  updateChat(chat: ChatModel, value: any) {
    return this.http.put<void>(
      environment.apiUrl + '/v1/chats/' + chat.id + '/update',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  loadChat(id: any) {
    return this.http.get<ChatModel>(
      environment.apiUrl + '/v1/chats/' + id,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  uploadMessageFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const request = new HttpRequest(
      "POST",
      environment.apiUrl + '/v1/chats/messages/upload-file',
      formData,
      {
        reportProgress: true,
        headers: new HttpHeaders(
          {
            'Authorization': 'Bearer ' + this.auth.getToken()!,
          }
        ),
      },
    );

    return this.http.request<FileModel>(request);
  }

  removeMessageFile(id: any) {
    return this.http.delete<void>(
      environment.apiUrl + '/messages-file/' + id,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  uploadFile(file: File) {
    const data = new FormData();
    data.append('file', file);

    return this.http.post(
      environment.apiUrl + '/v1/chats/messages/create-file',
      data,
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
            link.download = "My new file";
            link.click();

            return blob;
          },
        ),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker("errors.failed_downloading_the_document")));

          return EMPTY;
        }),
      );
  }

  downloadFile(file_message: FileModel) {
    return this.http.get(
      environment.apiUrl + '/v1/chats/file-messages/' + file_message.id + '/get-file',
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
            link.download = file_message.file_name ?? 'something';
            link.click();

            return blob;
          },
        ),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker('errors.failed_downloading_the_file')));

          return EMPTY;
        }),
      );
  }

  createLegalAssistanceRequest(chatId: number) {
    return this.http.post<any>(
      environment.apiUrl + '/v1/user-requests/',
      { chat_id: chatId },
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}
