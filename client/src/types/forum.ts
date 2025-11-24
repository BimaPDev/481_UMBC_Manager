export type Student = {
  id: number;
  name: string;
  email?: string;
};

export type Post = {
  id: number;
  student_id: number;
  student_name?: string;
  forum_title?: string;
  title: string;
  body_preview?: string;
  body?: string;
  tags?: string[];
  created_at: string; // ISO
  updated_at?: string;
  thread_id?: number;
};

export type SearchResponse = {
  items: Post[];
  page: number;
  page_size: number;
  total: number;
};
