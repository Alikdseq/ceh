import type { Category } from "./types";

export function flattenCategories(tree: Category[]): Category[] {
  const out: Category[] = [];
  function walk(nodes: Category[]) {
    for (const node of nodes) {
      out.push(node);
      if (node.children?.length) walk(node.children);
    }
  }
  walk(tree);
  return out;
}

export function findCategoryBySlug(tree: Category[], slug: string): Category | null {
  for (const node of tree) {
    if (node.slug === slug) return node;
    if (node.children?.length) {
      const found = findCategoryBySlug(node.children, slug);
      if (found) return found;
    }
  }
  return null;
}

export function findCategoryByPath(tree: Category[], slugs: string[]): Category | null {
  if (slugs.length === 0) return null;
  let nodes = tree;
  let current: Category | null = null;
  for (const slug of slugs) {
    current = nodes.find((n) => n.slug === slug) ?? null;
    if (!current) return null;
    nodes = current.children ?? [];
  }
  return current;
}

export function buildCategoryBreadcrumbs(
  tree: Category[],
  slugs: string[],
): { label: string; href?: string }[] {
  const items: { label: string; href?: string }[] = [{ label: "Каталог", href: "/catalog" }];
  let nodes = tree;
  let path = "/catalog";
  for (const slug of slugs) {
    const node = nodes.find((n) => n.slug === slug);
    if (!node) break;
    path += `/${slug}`;
    items.push({ label: node.h1 || node.name, href: path });
    nodes = node.children ?? [];
  }
  if (items.length > 0) {
    const last = items[items.length - 1];
    delete last.href;
  }
  return items;
}

export function getCategoryPathSlugs(tree: Category[], targetSlug: string): string[] {
  const path: string[] = [];
  function dfs(nodes: Category[], acc: string[]): boolean {
    for (const n of nodes) {
      const next = [...acc, n.slug];
      if (n.slug === targetSlug) {
        path.push(...next);
        return true;
      }
      if (n.children?.length && dfs(n.children, next)) return true;
    }
    return false;
  }
  dfs(tree, []);
  return path;
}
