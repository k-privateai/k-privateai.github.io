import { defineCollection, z } from "astro:content";

const posts = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    last_modified_at: z
      .union([z.string(), z.date()])
      .transform((val) => {
        if (val instanceof Date) return val;
        if (!val) return undefined;
        try {
          return new Date(val);
        } catch {
          return undefined;
        }
      })
      .optional(),
    categories: z.array(z.string()).optional(),
    tags: z.array(z.string()).optional(),
    toc: z.boolean().optional(),
    toc_label: z.string().optional(),
    toc_icon: z.string().optional(),
    toc_sticky: z.boolean().optional(),
    excerpt: z.string().optional(),
    slug: z.string().optional(),
    _legacyPermalink: z.string().optional(), // For URL mapping/redirects
  }),
});

export const collections = {
  posts,
};
