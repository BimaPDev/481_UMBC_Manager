import { useEffect, useState } from "react";
import { searchStudents } from "../api/forums";
import type { Student } from "../types/forum";

type FiltersValue = {
  student_id: number | null;
  tag: string;
  from: string;
  to: string;
};

export default function Filters({
  value,
  onChange,
}: {
  value: FiltersValue;
  onChange: (v: FiltersValue) => void;
}) {
  const [studentQuery, setStudentQuery] = useState("");
  const [students, setStudents] = useState<Student[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);

  useEffect(() => {
    let ignore = false;
    async function run() {
      if (!studentQuery.trim()) {
        setStudents([]);
        return;
      }
      setLoadingStudents(true);
      try {
        const res = await searchStudents(studentQuery);
        if (!ignore) setStudents(res);
      } finally {
        if (!ignore) setLoadingStudents(false);
      }
    }
    run();
    return () => {
      ignore = true;
    };
  }, [studentQuery]);

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
      {/* Student filter */}
      <div className="relative">
        <label className="mb-1 block text-xs font-medium text-slate-600">
          Student
        </label>
        <input
          value={studentQuery}
          onChange={(e) => setStudentQuery(e.target.value)}
          placeholder="Type a name/email"
          className="w-full rounded-lg border bg-white px-3 py-2 text-sm"
        />
        {(loadingStudents || students.length > 0) && (
          <div className="absolute mt-1 w-full rounded-lg border bg-white shadow">
            {loadingStudents && (
              <div className="p-2 text-xs text-slate-500">Searching…</div>
            )}
            {!loadingStudents &&
              students.map((s) => (
                <button
                  key={s.id}
                  onClick={() => {
                    onChange({ ...value, student_id: s.id });
                    setStudentQuery(s.name);
                    setStudents([]);
                  }}
                  className="block w-full px-3 py-2 text-left text-sm hover:bg-slate-50"
                >
                  <div className="font-medium">{s.name}</div>
                  {s.email && (
                    <div className="text-xs text-slate-500">{s.email}</div>
                  )}
                </button>
              ))}
            {!loadingStudents && students.length === 0 && (
              <div className="p-2 text-xs text-slate-500">No matches</div>
            )}
          </div>
        )}
        {value.student_id && (
          <button
            onClick={() => onChange({ ...value, student_id: null })}
            className="mt-1 text-xs text-slate-500 underline"
          >
            Clear student
          </button>
        )}
      </div>

      {/* Tag filter */}
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          Tag
        </label>
        <input
          value={value.tag}
          onChange={(e) => onChange({ ...value, tag: e.target.value })}
          placeholder="e.g. homework, exam"
          className="w-full rounded-lg border bg-white px-3 py-2 text-sm"
        />
      </div>

      {/* Date range */}
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          From
        </label>
        <input
          type="date"
          value={value.from}
          onChange={(e) => onChange({ ...value, from: e.target.value })}
          className="w-full rounded-lg border bg-white px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          To
        </label>
        <input
          type="date"
          value={value.to}
          onChange={(e) => onChange({ ...value, to: e.target.value })}
          className="w-full rounded-lg border bg-white px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}
