export interface UserModel {
  id: any;
  email: string;
  first_name: string;
  last_name: string;

  company_title?: string;
  job_title?: string;

  profile_image?: string;
  date_of_birth?: string;
}
