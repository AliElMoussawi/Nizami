import {UserModel} from '../../common/models/user.model';

export interface LoginResponse {
  access_token: string;
  user: UserModel;
}
