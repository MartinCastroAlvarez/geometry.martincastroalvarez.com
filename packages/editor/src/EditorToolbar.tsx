/**
 * Editor toolbar: mode options (Vertices/Edges/Erase), zoom out, clean, zoom in, Validate, Submit.
 */
import { Minus, Trash2, Plus, CheckCircle, Send, Pen, PenLine, Eraser } from "lucide-react";
import { Container, Toolbar, Button, Options, Option } from "@geometry/ui";
import { useLocale } from "@geometry/i18n";
import { EditorMode } from "./EditorMode";

const MODE_ICONS: Record<EditorMode, React.ReactNode> = {
    [EditorMode.Add]: <Pen size={14} className="shrink-0" aria-hidden />,
    [EditorMode.Connect]: <PenLine size={14} className="shrink-0" aria-hidden />,
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
                    <Options value={mode} onChange={(v) => onModeChange(v as EditorMode)} disabled={disabled}>
                        <Option name={EditorMode.Add}>{MODE_ICONS[EditorMode.Add]}</Option>
                        <Option name={EditorMode.Connect}>{MODE_ICONS[EditorMode.Connect]}</Option>
                        <Option name={EditorMode.Erase}>{MODE_ICONS[EditorMode.Erase]}</Option>
                    </Options>
                    {onZoomOut != null && (
                        <Button sm onClick={onZoomOut} icon={<Minus size={14} className="shrink-0" aria-hidden />} aria-label="Zoom out" />
                    )}
                    {onClean != null && (
                        <Button sm onClick={onClean} icon={<Trash2 size={14} className="shrink-0" aria-hidden />} aria-label="Clear" />
                    )}
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
