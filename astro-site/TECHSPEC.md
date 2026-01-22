# TECHSPEC_PLAN.md
## Jekyll → Astro Migration (Content-Preserving, Structure Rewrite)
Repository: k-privateai/k-privateai.github.io
Owner: You
Date: 2026-01-20 (America/Los_Angeles)

---

## 0. Principles (Non-negotiables)

- ✅ Preserve Markdown content (no manual edits to post bodies)
- ✅ Preserve URL structure as much as possible (SEO + link integrity)
- ✅ Remove Jekyll/Liquid/Ruby dependencies entirely
- ✅ Add interactivity only via React Islands (minimal JS)
- ✅ Split migration into phases: Safe-first → Optimize later

---

## 1. New Astro Project Bootstrap

### 1.1 Create Astro project
```bash
npm create astro@latest astro-site
cd astro-site
npm install

Choose:
	•	Template: Minimal
	•	TypeScript: Yes
	•	SSR: No (Static)
	•	Git: Yes

1.2 Add React (Islands)

npx astro add react

1.3 Add Markdown tooling dependencies (for migration scripts)

npm i -D gray-matter fast-glob js-yaml


⸻

2. URL / Build Format Strategy (SEO-critical)

2.1 Decide output URL format to match GitHub Pages + Jekyll behavior

Create/modify: astro.config.mjs
	•	Goal A (recommended): directory-style URLs like /posts/my-post/
	•	Use build.format = "directory" to emit /path/index.html
	•	Enforce trailing slash policy consistently

Edit file: astro.config.mjs

import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  integrations: [react()],
  build: {
    format: "directory", // /foo/ -> /foo/index.html
  },
  trailingSlash: "always", // enforce /foo/
});

If the existing site uses .html endings (e.g. /foo.html), switch:
	•	build.format: "file"
	•	trailingSlash: "never"

2.2 permalink variance handling

If Jekyll posts have custom permalink: per-file:
	•	Preserve by generating a “canonicalSlug” in migration script and mapping it to slug for Content Collections.
	•	If no permalink exists, default to date+title or category+title (matching previous patterns).

⸻

3. What NOT to bring over (Jekyll-only files)

Do not copy into Astro project:
	•	_config.yml
	•	Gemfile, Gemfile.lock
	•	.ruby-version
	•	_plugins/*.rb (replace with Astro config/integrations)
	•	any *.gemspec

⸻

4. Directory Mapping (Jekyll → Astro)

4.1 Markdown content (preserve bodies)
	•	_posts/ → src/content/posts/
	•	_pages/ → src/pages/ (convert to .astro wrapper if needed; see §7)

4.2 Includes/layouts
	•	_layouts/ → src/layouts/
	•	_includes/ → src/components/ (Astro components)

4.3 Data
	•	_data/*.yml → src/data/*.json (convert YAML → JSON)
	•	Keep YAML initially if conversion cost is high, but JSON is preferred.

4.4 Assets (two-stage plan)

Phase-1 (safe):
	•	assets/ → public/assets/ (keeps /assets/... paths working without Markdown edits)

Phase-2 (optimize):
	•	Migrate selected images into src/assets/ and use astro:assets + remark rewrite plugin (see §10)

⸻

5. Migration Scripts (Frontmatter + Liquid Removal + Date Safety)

Create directory: scripts/

5.1 Script A — Posts normalization + frontmatter cleanup + Liquid token rewrite

New file: scripts/migrate-posts.mjs

Responsibilities:
	1.	Ensure all posts have frontmatter
	2.	Inject date from filename if missing: YYYY-MM-DD-*.md
	3.	Remove Jekyll-only keys: layout, published, permalink (but store permalink in a new key if needed)
	4.	Rewrite common Liquid tokens in Markdown:
	•	{{ site.baseurl }} → ""
	•	{{ site.url }} → "" (or to a SITE_URL constant if needed)
	•	{% highlight lang %} blocks → fenced code blocks ```lang
	•	{% endhighlight %} → ```
	•	{% include ... %} → placeholder comment to be handled later

Implementation (minimal but practical):

import fs from "fs";
import path from "path";
import fg from "fast-glob";
import matter from "gray-matter";

const POSTS_DIR = "src/content/posts";

function inferDateFromFilename(file) {
  const base = path.basename(file);
  const m = base.match(/^(\d{4})-(\d{2})-(\d{2})-/);
  if (!m) return null;
  const [_, y, mo, d] = m;
  return `${y}-${mo}-${d}`;
}

function rewriteLiquid(content) {
  // 1) common site tokens
  content = content.replace(/\{\{\s*site\.baseurl\s*\}\}/g, "");
  content = content.replace(/\{\{\s*site\.url\s*\}\}/g, "");

  // 2) highlight blocks -> fenced code
  // {% highlight js %} ... {% endhighlight %}
  content = content.replace(/\{%\s*highlight\s+([a-zA-Z0-9_-]+)\s*%\}/g, "```$1");
  content = content.replace(/\{%\s*endhighlight\s*%\}/g, "```");

  // 3) include tags -> keep as explicit TODO marker for later manual/component replacement
  // We do NOT silently delete includes because it can remove meaning.
  content = content.replace(/\{%\s*include\s+([^%]+)\s*%\}/g, (m, p1) => {
    return `<!-- TODO: JEKYLL_INCLUDE ${p1.trim()} -->`;
  });

  // 4) remove leftover Liquid output tags safely (only trivial ones)
  // Keep non-trivial ones for manual review to avoid content loss.
  // Example: {{ page.title }} etc -> TODO marker
  content = content.replace(/\{\{\s*page\.[^}]+\}\}/g, (m) => `<!-- TODO: LIQUID ${m} -->`);

  return content;
}

(async function main() {
  const files = await fg(["**/*.md", "**/*.markdown"], { cwd: POSTS_DIR, absolute: true });

  for (const abs of files) {
    const raw = fs.readFileSync(abs, "utf8");
    const parsed = matter(raw);
    const data = { ...parsed.data };
    let content = parsed.content;

    // inject date if missing
    if (!data.date) {
      const inferred = inferDateFromFilename(abs);
      if (inferred) data.date = inferred;
    }

    // preserve permalink mapping if present
    if (data.permalink) {
      data._legacyPermalink = data.permalink; // keep for routing/redirect decisions
    }

    // remove Jekyll-only keys
    delete data.layout;
    delete data.permalink;
    delete data.published;

    // rewrite liquid patterns in body
    content = rewriteLiquid(content);

    const out = matter.stringify(content, data);
    fs.writeFileSync(abs, out, "utf8");
  }

  console.log(`Migrated ${files.length} post files in ${POSTS_DIR}`);
})();

5.2 Script B — YAML → JSON for _data

New file: scripts/migrate-data.mjs

import fs from "fs";
import path from "path";
import fg from "fast-glob";
import yaml from "js-yaml";

const IN_DIR = "src/data-yaml";
const OUT_DIR = "src/data";

fs.mkdirSync(OUT_DIR, { recursive: true });

(async function main() {
  const files = await fg(["**/*.yml", "**/*.yaml"], { cwd: IN_DIR, absolute: true });
  for (const abs of files) {
    const raw = fs.readFileSync(abs, "utf8");
    const obj = yaml.load(raw);
    const name = path.basename(abs).replace(/\.(yml|yaml)$/i, ".json");
    fs.writeFileSync(path.join(OUT_DIR, name), JSON.stringify(obj, null, 2), "utf8");
  }
  console.log(`Converted ${files.length} data files to JSON.`);
})();


⸻

6. Content Collections (Posts) + Slug Control

6.1 Define collections

New file: src/content/config.ts

import { defineCollection, z } from "astro:content";

export const collections = {
  posts: defineCollection({
    schema: z.object({
      title: z.string(),
      date: z.coerce.date(),
      tags: z.array(z.string()).optional(),
      categories: z.array(z.string()).optional(),
      excerpt: z.string().optional(),
      _legacyPermalink: z.string().optional(),
    }),
  }),
};

6.2 Explicit slug override strategy (for permalink preservation)

If you must force a slug:
	•	Use frontmatter field slug: in the post
	•	Or compute it during migration and write slug: to frontmatter

Rule:
	•	If _legacyPermalink exists, write slug derived from it
	•	Else use default post.slug

(Implemented via scripts/migrate-posts.mjs extension if needed.)

⸻

7. Pages (Jekyll _pages → Astro src/pages)

7.1 Strategy options
	•	If _pages/*.md are simple content pages: copy to src/pages/*.md
	•	If pages depend on Liquid/layout loops: convert to .astro and render from data sources.

7.2 Action
	•	Copy files:
	•	Jekyll/_pages/*.md → Astro/src/pages/*.md
	•	Run a liquid rewrite pass (optional) using a similar script:
	•	Replace {{ }} and {% %} with TODO markers

⸻

8. Routing Implementation (Posts, Tags, Posts Index)

8.1 Post detail

New file: src/pages/posts/[...slug].astro

---
import { getCollection } from "astro:content";
import PostLayout from "../../layouts/PostLayout.astro";

export async function getStaticPaths() {
  const posts = await getCollection("posts");
  return posts.map((post) => ({
    params: { slug: post.slug },
    props: { post },
  }));
}

const { post } = Astro.props;
---
<PostLayout frontmatter={post.data}>
  <post.Content />
</PostLayout>

8.2 Tags archive

New file: src/pages/tags/[tag].astro

---
import { getCollection } from "astro:content";

export async function getStaticPaths() {
  const posts = await getCollection("posts");
  const tags = new Set();
  posts.forEach((p) => (p.data.tags || []).forEach((t) => tags.add(t)));
  return [...tags].map((tag) => ({ params: { tag } }));
}

const { tag } = Astro.params;
const posts = (await getCollection("posts")).filter((p) => p.data.tags?.includes(tag));
---
<h1>#{tag}</h1>
<ul>
  {posts.map((p) => (
    <li><a href={`/posts/${p.slug}/`}>{p.data.title}</a></li>
  ))}
</ul>

8.3 Posts index + Pagination (added)

New file: src/pages/posts/[page].astro

---
import { getCollection } from "astro:content";

export async function getStaticPaths({ paginate }) {
  const posts = await getCollection("posts");
  // newest first
  posts.sort((a, b) => +b.data.date - +a.data.date);
  return paginate(posts, { pageSize: 10 });
}

const { page } = Astro.props;
---
<h1>Posts</h1>
<ul>
  {page.data.map((p) => (
    <li><a href={`/posts/${p.slug}/`}>{p.data.title}</a></li>
  ))}
</ul>

<nav>
  {page.url.prev && <a href={page.url.prev}>Prev</a>}
  {page.url.next && <a href={page.url.next}>Next</a>}
</nav>


⸻

9. Layouts + Components (Liquid replacement)

9.1 Base layout with SEO hooks

New file: src/layouts/BaseLayout.astro

---
import SeoHead from "../components/SeoHead.astro";
const { title, description, canonical, image } = Astro.props;
---
<html lang="en">
  <head>
    <SeoHead
      title={title}
      description={description}
      canonical={canonical}
      image={image}
    />
  </head>
  <body>
    <slot />
  </body>
</html>

9.2 Post layout

New file: src/layouts/PostLayout.astro

---
import BaseLayout from "./BaseLayout.astro";
const { frontmatter } = Astro.props;

const title = frontmatter.title;
const description = frontmatter.excerpt ?? "";
const canonical = Astro.url; // will become absolute with site config if set
---
<BaseLayout title={title} description={description} canonical={canonical}>
  <article>
    <header>
      <h1>{frontmatter.title}</h1>
      <time datetime={frontmatter.date.toISOString()}>
        {frontmatter.date.toLocaleDateString()}
      </time>
    </header>
    <slot />
  </article>
</BaseLayout>


⸻

10. SEO Migration (jekyll-seo-tag replacement)

10.1 Minimal SEO head component

New file: src/components/SeoHead.astro

---
const {
  title,
  description = "",
  canonical,
  image,
} = Astro.props;

const canonicalUrl = typeof canonical === "string"
  ? canonical
  : (canonical?.toString?.() ?? "");
---
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />

{title && <title>{title}</title>}
{description && <meta name="description" content={description} />}

{canonicalUrl && <link rel="canonical" href={canonicalUrl} />}

<meta property="og:type" content="website" />
{title && <meta property="og:title" content={title} />}
{description && <meta property="og:description" content={description} />}
{canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
{image && <meta property="og:image" content={image} />}

<meta name="twitter:card" content="summary_large_image" />
{title && <meta name="twitter:title" content={title} />}
{description && <meta name="twitter:description" content={description} />}
{image && <meta name="twitter:image" content={image} />}

10.2 Site-wide canonical correctness

Edit file: astro.config.mjs
Add site: for absolute canonical URLs.

export default defineConfig({
  site: "https://k-privateai.github.io",
  // ...
});

10.3 Redirect plan (if URL changes are unavoidable)
	•	Create static redirect files in public/ for critical legacy URLs.
	•	If scale is large, generate redirect HTML files via a script:
	•	public/old/path/index.html → meta refresh to new path.

⸻

11. Assets Strategy (Safe-first, Optimize later)

11.1 Phase-1: Keep paths stable
	•	Copy Jekyll/assets/** → Astro/public/assets/**
	•	Do NOT change Markdown image URLs

11.2 Phase-2: Enable optimization without Markdown edits (optional)

Add a remark plugin that rewrites /assets/... to an importable asset strategy OR keep public assets but add Image component usage in Astro pages.

Decision gate:
	•	Only do Phase-2 if Lighthouse indicates image payload bottlenecks.

⸻

12. React Islands (minimal)

12.1 Search component

New file: src/components/Search.jsx

import { useMemo, useState } from "react";

export default function Search({ items = [] }) {
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return items;
    return items.filter((x) => x.title.toLowerCase().includes(s));
  }, [q, items]);

  return (
    <div>
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search posts"
      />
      <ul>
        {filtered.map((p) => (
          <li key={p.url}><a href={p.url}>{p.title}</a></li>
        ))}
      </ul>
    </div>
  );
}

12.2 Wire it in posts index (optional)

Edit file: src/pages/posts/[page].astro
	•	Add JSON list for the current page only
	•	Use island client:idle

⸻

13. QA / Verification (must run)

13.1 Build checks

npm run build
npm run preview

13.2 Link integrity checks
	•	Confirm posts open and render
	•	Confirm tags pages render for existing tags
	•	Confirm /assets/... images load
	•	Confirm canonical tags exist and correct

13.3 SEO regression checks
	•	Validate:
	•	title, description, canonical
	•	og:*, twitter:*
	•	Ensure sitemap.xml strategy (optional):
	•	Add integration later if needed.

⸻

14. Execution Order (Phased)

Phase 1 (Stabilize URLs + content render)
	1.	Create Astro project + config (build.format, trailingSlash, site)
	2.	Copy posts/pages/assets/data into mapped folders
	3.	Run scripts/migrate-posts.mjs
	4.	Implement collections + post routes
	5.	Implement BaseLayout + PostLayout
	6.	Validate build + preview

Phase 2 (Feature parity: tags, pagination, data pages)
	7.	Implement tags pages
	8.	Implement posts pagination
	9.	Convert _data → JSON and wire events/committee/membership pages

Phase 3 (Optional improvements)
	10.	React islands for search/menu
	11.	Image optimization phase-2
	12.	Redirect generation for any unavoidable URL changes

⸻

15. Done Definition (DoD)
	•	Liquid tags removed or converted to explicit TODO markers (no silent loss)
	•	Posts render via Astro Content Collections
	•	URLs follow chosen build.format and trailingSlash policy
	•	Canonical/OG/Twitter meta implemented
	•	Assets served at existing /assets/... paths
	•	Tags + pagination working
	•	Build + preview succeeds

⸻


