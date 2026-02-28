/**
 * Editor toolbar: mode buttons (Connect/Add/Erase/Move), trash, zoom, Validate, Submit.
 * Mode buttons are mutually exclusive; the active one gets the primary prop.
 */
import { Minus, Trash2, Plus, CheckCircle, Send, Pen, PenLine, Hand, Eraser } from "lucide-react";
import { Container, Toolbar, Button } from "@geometry/ui";
import { useLocale } from "@geometry/i18n";
import { EditorMode } from "./EditorMode";

const MODE_ICONS: Record<EditorMode, React.ReactNode> = {
    [EditorMode.Add]: <Pen size={14} className="shrink-0" aria-hidden />,
    [EditorMode.Connect]: <PenLine size={14} className="shrink-0" aria-hidden />,
    [EditorMode.Move]: <Hand size={14} className="shrink-0" aria-hidden />,
    [EditorMode.Erase]: <Eraser size={14} className="shrink-0" aria-hidden />,
};

export interface EditorToolbarProps {
    mode?: EditorMode;
    onModeChange: (mode: EditorMode) => void;
    onZoomOut?: () => void;
    onClean?: () => void;
    onZoomIn?: () => void;
    onValidate?: () => void;
    onSubmit?: () => void;
    /** When true, Validate and Submit buttons are disabled (e.g. while a request is pending). */
    disabled?: boolean;
}

export const EditorToolbar = ({
    mode = EditorMode.Connect,
    onModeChange,
    onZoomOut,
    onClean,
    onZoomIn,
    onValidate,
    onSubmit,
    disabled = false,
}: EditorToolbarProps) => {
    const { t } = useLocale();
    return (
        <>
            <Container name="geometry-editor-toolbar" middle center spaced>
                <Toolbar center>
                    {/* Add vertices connected by edges (Connect) */}
                    <Button
                        sm
                        primary={mode === EditorMode.Connect}
                        icon={MODE_ICONS[EditorMode.Connect]}
                        onClick={() => onModeChange(EditorMode.Connect)}
                        disabled={disabled}
                        aria-label="Add vertices connected by edges"
                    />
                    {/* Add vertices only (Add) */}
                    <Button
                        sm
                        primary={mode === EditorMode.Add}
                        icon={MODE_ICONS[EditorMode.Add]}
                        onClick={() => onModeChange(EditorMode.Add)}
                        disabled={disabled}
                        aria-label="Add vertices"
                    />
                    {/* Erase mode */}
                    <Button
                        sm
                        primary={mode === EditorMode.Erase}
                        icon={MODE_ICONS[EditorMode.Erase]}
                        onClick={() => onModeChange(EditorMode.Erase)}
                        disabled={disabled}
                        aria-label="Erase"
                    />
                    {/* Trash: clear everything */}
                    {onClean != null && (
                        <Button
                            sm
                            confirm={t("editor.clearConfirm")}
                            onClick={onClean}
                            icon={<Trash2 size={14} className="shrink-0" aria-hidden />}
                            aria-label="Clear"
                        />
                    )}
                    {/* Zoom out */}
                    {onZoomOut != null && (
                        <Button sm onClick={onZoomOut} icon={<Minus size={14} className="shrink-0" aria-hidden />} aria-label="Zoom out" />
                    )}
                    {/* Move (hand) */}
                    <Button
                        sm
                        primary={mode === EditorMode.Move}
                        icon={MODE_ICONS[EditorMode.Move]}
                        onClick={() => onModeChange(EditorMode.Move)}
                        disabled={disabled}
                        aria-label="Move"
                    />
                    {/* Zoom in */}
                    {onZoomIn != null && (
                        <Button sm onClick={onZoomIn} icon={<Plus size={14} className="shrink-0" aria-hidden />} aria-label="Zoom in" />
                    )}
                </Toolbar>
            </Container>
            {(onValidate != null || onSubmit != null) && (
                <Container name="geometry-editor-toolbar-actions" middle center spaced>
                    <Toolbar center>
                        {onValidate != null && (
                            <Button sm onClick={onValidate} disabled={disabled} icon={<CheckCircle size={14} className="shrink-0" aria-hidden />}>
                                {t("editor.validate")}
                            </Button>
                        )}
                        {onSubmit != null && (
                            <Button sm primary onClick={onSubmit} disabled={disabled} icon={<Send size={14} className="shrink-0" aria-hidden />}>
                                {t("editor.submit")}
                            </Button>
                        )}
                    </Toolbar>
                </Container>
            )}
        </>
    );
};
