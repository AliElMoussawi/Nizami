export interface MessageModel {
  id: number | null;
  uuid?: string | null;
  text: string;
  role?: "system" | "user";
  chat_id?: any;
  create_at?: any;

  language?: string;
  show_translation_disclaimer?: boolean;
  translation_disclaimer_language?: string;

  messageFiles?: FileModel[] | null;
  message_file_ids?: number[] | null;
}

export interface FileModel {
  id?: any;
  file_name?: string;
  size?: any;
  extension?: string;

  file?: File;
}
