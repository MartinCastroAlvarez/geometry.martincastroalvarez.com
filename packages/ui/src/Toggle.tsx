import { Button } from "./Button";

export interface ToggleProps {
  value: string;
  options: string[];
  onChange: (value: string) => void;
  sm?: boolean;
}

/**
 * Toggle cycles through options on click. Wrapper around Button.
 * Displays current value; on click selects next option and calls onChange.
 */
export const Toggle = ({ value, options, onChange, sm = false }: ToggleProps) => {
  if (options.length === 0) return null;

  const currentIndex = options.indexOf(value);
  const index = currentIndex >= 0 ? currentIndex : 0;

  const handleClick = () => {
    const nextIndex = (index + 1) % options.length;
    const nextValue = options[nextIndex];
    onChange(nextValue);
  };

  return (
    <Button onClick={handleClick} sm={sm}>
      {value}
    </Button>
  );
};
