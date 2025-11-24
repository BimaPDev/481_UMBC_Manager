import { api } from "./client";
import type { SearchResponse, Post, Student } from "../types/forum";

export type SearchParams = {
  q?: string;
  student_id?: number | null;
  tag?: string | null;
  from?: string | null; // YYYY-MM-DD
  to?: string | null; // YYYY-MM-DD
  page?: number;
  page_size?: number;
};

export async function searchForums(params: SearchParams) {
  // CHANGE THIS PATH to match FastAPI
  const { data } = await api.get<SearchResponse>("/api/forums/search", {
    params,
  });
  return data;
}

export async function getPost(id: number) {
  // CHANGE THIS PATH to match FastAPI
  const { data } = await api.get<Post>(`/api/forums/posts/${id}`);
  return data;
}

export async function searchStudents(query: string) {
  // OPTIONAL endpoint for autocomplete
  const { data } = await api.get<Student[]>("/api/students", {
    params: { search: query },
  });
  return data;
}
