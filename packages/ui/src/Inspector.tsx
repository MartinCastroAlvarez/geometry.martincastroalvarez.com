/**
 * Read-only JSON inspector: displays arbitrary JSON inside a Container using react-json-view.
 *
 * Context: Used to inspect polygon data (boundary, obstacles) and other structured data.
 * For very large payloads the displayed text is truncated to avoid memory issues; a Copy
 * button always allows copying the full JSON. Edit/add/delete are disabled.
 *
 * Example:
 *   <Inspector data={polygon.toDict()} />
 */

import React, { useCallback, useMemo } from "react";
import ReactJson from "react-json-view";
import { Theme, useTheme } from "@geometry/theme";
import { useLocale } from "@geometry/i18n";
import { Scrollable } from "./Scrollable";
import { Button } from "./Button";

export interface InspectorProps {
    /** JSON-serializable data to display (object or array). Null/undefined treated as {}. */
    data: object | null | undefined;
    /** Max height of the JSON view container in pixels; overflow scrolls on the y-axis. Default 300. */
    size?: number;
    /** Max string length before collapsing in the JSON view (small payloads only). Default 25. */
    maxLength?: number;
    /** Max characters to render in the DOM; above this the view is truncated and Copy is used for full JSON. Default 50000. */
    displayLimit?: number;
}

/** Default max string length before collapsing in the JSON inspector. */
const DEFAULT_INSPECTOR_MAX_LENGTH = 25;

/** Default max characters to render; larger payloads are truncated to avoid memory pressure. */
const DEFAULT_DISPLAY_LIMIT = 50_000;

/** react-json-view base16 theme: light theme (dark text) for light mode, dark theme (light text) for dark mode. */
const JSON_VIEW_THEME_LIGHT = "bright";
const JSON_VIEW_THEME_DARK = "monokai";

/** Data attribute for inspector panel; apps add CSS so inner elements use theme and panel background is visible. */
export const INSPECTOR_LIGHT_ATTR = "data-inspector-light";
export const INSPECTOR_CONTENT_ATTR = "data-inspector-content";

function sanitizeForDisplay(raw: object | null | undefined): object {
    const obj =
        raw === null || raw === undefined
            ? {}
            : typeof raw === "object" && raw !== null
              ? raw
              : { value: raw };
    try {
        return JSON.parse(JSON.stringify(obj)) as object;
    } catch {
        return { "(unserializable)": "e.g. circular reference" };
    }
}

export const Inspector: React.FC<InspectorProps> = ({
    data,
    size = 300,
    maxLength = DEFAULT_INSPECTOR_MAX_LENGTH,
    displayLimit = DEFAULT_DISPLAY_LIMIT
}) => {
    const { theme, getColor } = useTheme();
    const { t } = useLocale();
    const isLight = theme === Theme.Light;

    const safeData = useMemo(() => sanitizeForDisplay(data), [data]);

    const displayInfo = useMemo(() => {
        try {
            const full = JSON.stringify(safeData, null, 2);
            if (full.length <= displayLimit) return { large: false as const };
            return { large: true as const, displayText: full.slice(0, displayLimit) };
        } catch {
            return { large: false as const };
        }
    }, [safeData, displayLimit]);

    const copyFullJson = useCallback(() => {
        try {
            const text =
                data != null && typeof data === "object"
                    ? JSON.stringify(data, null, 2)
                    : JSON.stringify(safeData, null, 2);
            void navigator.clipboard.writeText(text);
        } catch {
            try {
                void navigator.clipboard.writeText(JSON.stringify(safeData, null, 2));
            } catch {
                /* no-op */
            }
        }
    }, [data, safeData]);

    const truncationSuffix = `\n\n... ${t("inspector.truncated")}`;

    return (
        <div className="flex flex-col gap-1 w-full">
            <div className="flex justify-end">
                <Button xs onClick={copyFullJson} aria-label={t("common.copy")}>
                    {t("common.copy")}
                </Button>
            </div>
            <Scrollable height={size} left>
                <div
                    {...{
                        [INSPECTOR_CONTENT_ATTR]: "",
                        ...(isLight && { [INSPECTOR_LIGHT_ATTR]: "" }),
                        style: {
                            background: getColor("--color-inspector-bg"),
                            color: getColor("--color-text"),
                        },
                    }}
                >
                    {displayInfo.large ? (
                        <pre
                            style={{
                                margin: 0,
                                padding: 10,
                                fontSize: "10px",
                                whiteSpace: "pre-wrap",
                                wordBreak: "break-word"
                            }}
                        >
                            {displayInfo.displayText}
                            {truncationSuffix}
                        </pre>
                    ) : (
                        <ReactJson
                            src={safeData}
                            name={false}
                            theme={isLight ? JSON_VIEW_THEME_LIGHT : JSON_VIEW_THEME_DARK}
                            indentWidth={2}
                            enableClipboard
                            displayDataTypes
                            collapsed={false}
                            collapseStringsAfterLength={maxLength}
                            style={{
                                margin: 0,
                                padding: 10,
                                fontSize: "10px"
                            }}
                        />
                    )}
                </div>
            </Scrollable>
        </div>
    );
};
