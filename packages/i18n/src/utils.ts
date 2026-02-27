/**
 * Helpers for translation lookups and variable interpolation.
 *
 * Context: getNested resolves dot-path keys (e.g. "section.sub.key") on a nested object and returns a string or undefined.
 * interpolate replaces {{varName}} in a template string with values from vars; used by LocaleProvider's t().
 *
 * Example:
 *   getNested(translations, "form.submit");  // "Submit" or undefined
 *   interpolate("Hello, {{name}}!", { name: "World" });  // "Hello, World!"
 */
type NestedRecord = Record<string, unknown>;

export const getNested = (obj: NestedRecord, path: string): string | undefined => {
  const parts = path.split(".");
  let current: unknown = obj;
  for (const part of parts) {
    if (current == null || typeof current !== "object") return undefined;
    current = (current as NestedRecord)[part];
  }
  return typeof current === "string" ? current : undefined;
};

export const interpolate = (template: string, vars: Record<string, string | number>): string => {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key) => String(vars[key] ?? ""));
};
