// Dev server only: pages that are files (academy/…/lesson.html) are routes ending in ".html"; the dev server expects
// them with a trailing slash. The static build is not affected (see the file-pages step in astro.config.mjs).
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware((context, next) => {
  const { pathname } = context.url;
  if (import.meta.env.DEV && pathname.endsWith('.html') && !pathname.endsWith('/index.html')) return context.rewrite(pathname + '/');
  return next();
});
