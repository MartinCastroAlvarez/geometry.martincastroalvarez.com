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
  icon?: React.ReactNode;
  sm?: boolean;
}

export const Toggle = ({ value, options, onChange, icon, sm = false }: ToggleProps) => {
  if (options.length === 0) return null;

  const currentIndex = options.indexOf(value);
  const index = currentIndex >= 0 ? currentIndex : 0;

  const handleClick = useCallback(() => {
    const nextIndex = (index + 1) % options.length;
    const nextValue = options[nextIndex];
    onChange(nextValue);
  }, [index, options, onChange]);

  return (
    <Button onClick={handleClick} icon={icon} sm={sm}>
      {value}
    </Button>
  );
};
