"use client";

import { useEffect, useState } from "react";

type BackendStatus = {
  root: { message: string } | null;
  db: { db: number } | null;
  error: string | null;
};

const BACKEND_HOST =
  process.env.NEXT_PUBLIC_BACKEND_HOST || "http://localhost:8000";

export default function Home() {
  const [status, setStatus] = useState<BackendStatus>({
    root: null,
    db: null,
    error: null,
  });

  useEffect(() => {
    async function getBackendStatus() {
      try {
        const [rootRes, dbRes] = await Promise.all([
          fetch(BACKEND_HOST),
          fetch(`${BACKEND_HOST}/db-check`),
        ]);

        if (!rootRes.ok || !dbRes.ok) {
          throw new Error(`status ${rootRes.status}/${dbRes.status}`);
        }

        setStatus({
          root: await rootRes.json(),
          db: await dbRes.json(),
          error: null,
        });
      } catch (e) {
        setStatus({ root: null, db: null, error: String(e) });
      }
    }

    getBackendStatus();
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-zinc-50 p-8 font-sans dark:bg-black">
      <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
        vamo_1 接続確認
      </h1>

      {status.error ? (
        <p className="max-w-md text-center text-red-500">
          バックエンドに接続できませんでした: {status.error}
        </p>
      ) : (
        <div className="flex flex-col items-center gap-2 text-black dark:text-zinc-50">
          <p>backend: {JSON.stringify(status.root)}</p>
          <p>db-check: {JSON.stringify(status.db)}</p>
        </div>
      )}
    </div>
  );
}
