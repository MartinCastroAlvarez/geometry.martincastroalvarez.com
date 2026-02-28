/**
 * Editor toolbar: zoom out, clean (trash), zoom in, Validate, Submit.
 * Uses Container, Toolbar and Button from @geometry/ui and lucide-react icons.
 */
import { Minus, Trash2, Plus, CheckCircle, Send } from "lucide-react";
import { Container, Toolbar, Button } from "@geometry/ui";
import { useLocale } from "@geometry/i18n";

export interface EditorToolbarProps {
    onZoomOut: () => void;
    onClean: () => void;
    onZoomIn: () => void;
    onValidate?: () => void;
    onSubmit?: () => void;
    /** When true, Validate and Submit buttons are disabled (e.g. while a request is pending). */
    disabled?: boolean;
}

export const EditorToolbar = ({
    onZoomOut,
    onClean,
    onZoomIn,
    onValidate,
    onSubmit,
    disabled = false,
}: EditorToolbarProps) => {
    const { t } = useLocale();
    return (
        <Container name="geometry-editor-toolbar">
            <Toolbar right>
                <Button sm onClick={onZoomOut} icon={<Minus size={14} className="shrink-0 text-slate-200" aria-hidden />} aria-label="Zoom out" />
                <Button sm onClick={onClean} icon={<Trash2 size={14} className="shrink-0 text-slate-200" aria-hidden />} aria-label="Clear" />
                <Button sm onClick={onZoomIn} icon={<Plus size={14} className="shrink-0 text-slate-200" aria-hidden />} aria-label="Zoom in" />
                {onValidate != null && (
                    <Button sm onClick={onValidate} disabled={disabled} icon={<CheckCircle size={14} className="shrink-0 text-slate-200" aria-hidden />}>
                        {t("editor.validate")}
                    </Button>
                )}
                {onSubmit != null && (
                    <Button sm primary onClick={onSubmit} disabled={disabled} icon={<Send size={14} className="shrink-0 text-slate-200" aria-hidden />}>
                        {t("editor.optimize")}
                    </Button>
                )}
            </Toolbar>
        </Container>
    );
};
