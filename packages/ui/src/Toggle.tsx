/**
 * Cycle-through-options toggle: displays current value, click advances to next and calls onChange.
 *
 * Context: Wraps Button; options array defines order. Index is derived from value; each click
 * selects options[(index + 1) % length]. Supports icon and sm for Button appearance.
 *
 * Example:
 *   <Toggle value={theme} options={['light','dark','system']} onChange={setTheme} />
 */

import React, { useCallback } from "react";
import { Button } from "./Button";

export interface ToggleProps {
  value: string;
  options: string[];
  onChange: (value: string) => void;
  /** Static icon shown for all options, or function (currentValue) => icon for per-option icon */
  icon?: React.ReactNode | ((value: string) => React.ReactNode);
  /** Optional label for the button (e.g. localized); defaults to value */
  formatLabel?: (value: string) => React.ReactNode;
  sm?: boolean;
}

export const Toggle = ({ value, options, onChange, icon, formatLabel, sm = false }: ToggleProps) => {
  if (options.length === 0) return null;

  const currentIndex = options.indexOf(value);
  const index = currentIndex >= 0 ? currentIndex : 0;

  const handleClick = useCallback(() => {
    const nextIndex = (index + 1) % options.length;
    const nextValue = options[nextIndex];
    onChange(nextValue);
  }, [index, options, onChange]);

  const resolvedIcon = icon === undefined ? undefined : typeof icon === "function" ? icon(value) : icon;
  const label = formatLabel ? formatLabel(value) : value;

  return (
    <Button onClick={handleClick} icon={resolvedIcon} sm={sm}>
      {label}
    </Button>
  );
};
