import {ChatModel} from './chat.model';

export interface ChatGroupModel {
  id: number;
  created_at: any;

  chats: ChatModel[];
}
