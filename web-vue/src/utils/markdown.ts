import { unified } from "unified";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeHighlight from "rehype-highlight";
import rehypeRaw from "rehype-raw";
import rehypeStringify from "rehype-stringify";

function postProcessHtml(html: string) {
  return html
    .replace(
      /<pre><code class="hljs language-(\w+)">/g,
      '<pre class="code-block" data-language="$1"><code class="hljs language-$1">',
    )
    .replace(/<pre><code(?! class="hljs)([^>]*)>/g, '<pre class="ascii-diagram"><code$1>')
    .replace(/<table>/g, '<div class="table-scroll"><table>')
    .replace(/<\/table>/g, "</table></div>")
    .replace(/<blockquote>/, '<blockquote class="hero-callout">')
    .replace(/<h1>.*?<\/h1>\n?/s, "")
    .replace(
      /<ol start="(\d+)">/g,
      (_match, start) => `<ol style="counter-reset:step-counter ${Number.parseInt(start, 10) - 1}">`,
    );
}

export function renderMarkdown(markdown: string) {
  const html = unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeHighlight, { detect: false, ignoreMissing: true })
    .use(rehypeStringify)
    .processSync(markdown);

  return postProcessHtml(String(html));
}
