/**
 * Options: mutually exclusive option group. One Option selected at a time.
 * Option looks like a Button; when parent passes disabled, Option grays out but remains clickable.
 *
 * Example:
 *   <Options value={mode} onChange={setMode}>
 *     <Option name="a">Vertices</Option>
 *     <Option name="b">Edges</Option>
 *   </Options>
 */

import React, { createContext, useCallback, useContext } from "react";

interface OptionsContextValue {
    value: string;
    onChange: (name: string) => void;
    disabled?: boolean;
}

const OptionsContext = createContext<OptionsContextValue | null>(null);

export interface OptionsProps {
    value?: string;
    onChange: (value: string) => void;
    disabled?: boolean;
    children: React.ReactNode;
}

export const Options: React.FC<OptionsProps> = ({ value, onChange, disabled = false, children }) => {
    const optionNames = React.Children.toArray(children)
        .filter((child): child is React.ReactElement<OptionProps> => React.isValidElement(child) && (child.type === Option))
        .map((child) => (child.props as OptionProps).name);
    const selected = value != null && value !== "" ? value : optionNames[0] ?? "";

    const ctx: OptionsContextValue = {
        value: selected,
        onChange,
        disabled,
    };

    return (
        <OptionsContext.Provider value={ctx}>
            <div className="flex flex-row flex-wrap items-center gap-2">
                {children}
            </div>
        </OptionsContext.Provider>
    );
};

Options.displayName = "Options";

export interface OptionProps {
    name: string;
    children?: React.ReactNode;
}

export const Option: React.FC<OptionProps> = ({ name, children }) => {
    const ctx = useContext(OptionsContext);
    const selected = ctx?.value === name;
    const disabled = ctx?.disabled === true;
    const onChange = ctx?.onChange;

    const handleClick = useCallback(() => {
        if (onChange) onChange(name);
    }, [name, onChange]);

    const baseClasses =
        "appearance-none inline-flex flex-row items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-2 focus-visible:ring-offset-ring cursor-pointer border py-1 px-6 text-xs";
    const selectedClasses = selected
        ? "border-slate-300 bg-transparent text-primary"
        : "border-slate-300 bg-transparent text-primary opacity-30 hover:opacity-100 hover:bg-surface active:bg-surface-active";
    const disabledClasses = disabled ? "opacity-50" : "";

    return (
        <button
            type="button"
            onClick={handleClick}
            className={`geometry-option ${baseClasses} ${selectedClasses} ${disabledClasses}`.trim()}
            aria-pressed={selected}
        >
            <span className="flex flex-row flex-nowrap items-center gap-2">
                {children}
            </span>
        </button>
    );
};

Option.displayName = "Option";
