import { useEffect } from "react";

const DEFAULT_TITLE = "Агора";
const DEFAULT_DESCRIPTION =
  "Агора — душевный собеседник в Telegram. Разберем, что происходит.";

export function usePageMeta(title?: string, description?: string) {
  useEffect(() => {
    document.title = title ? `${title} · Агора` : DEFAULT_TITLE;
    const meta = document.querySelector('meta[name="description"]');
    if (meta) {
      meta.setAttribute("content", description || DEFAULT_DESCRIPTION);
    }
  }, [title, description]);
}
