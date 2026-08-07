import { describe, expect, it } from "vitest";
import { renderMarkdown } from "./markdown";

describe("renderMarkdown", () => {
  it("renders GFM tables inside a scroll wrapper", () => {
    const html = renderMarkdown("| A | B |\n| - | - |\n| 1 | 2 |");

    expect(html).toContain('<div class="table-scroll"><table>');
    expect(html).toContain("<td>1</td>");
  });

  it("removes the first h1 because page headers already show the title", () => {
    const html = renderMarkdown("# Lesson title\n\n## Details\n\nBody");

    expect(html).not.toContain("<h1>Lesson title</h1>");
    expect(html).toContain("<h2>Details</h2>");
  });

  it("adds code block language metadata for highlighted fences", () => {
    const html = renderMarkdown("```python\nprint('ok')\n```");

    expect(html).toContain('class="code-block"');
    expect(html).toContain('data-language="python"');
    expect(html).toContain("print");
  });

  it("marks the first blockquote as a hero callout", () => {
    const html = renderMarkdown("> Important idea");

    expect(html).toContain('<blockquote class="hero-callout">');
  });
});
