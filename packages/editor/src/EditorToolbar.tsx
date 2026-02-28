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
                <Button onClick={onZoomOut} icon={<Minus className="size-4 shrink-0 text-slate-200" aria-hidden />} aria-label="Zoom out" />
                <Button onClick={onClean} icon={<Trash2 className="size-4 shrink-0 text-slate-200" aria-hidden />} aria-label="Clear" />
                <Button onClick={onZoomIn} icon={<Plus className="size-4 shrink-0 text-slate-200" aria-hidden />} aria-label="Zoom in" />
                {onValidate != null && (
                    <Button onClick={onValidate} disabled={disabled} icon={<CheckCircle className="size-4 shrink-0 text-slate-200" aria-hidden />} sm>
                        {t("editor.validate")}
                    </Button>
                )}
                {onSubmit != null && (
                    <Button onClick={onSubmit} disabled={disabled} icon={<Send className="size-4 shrink-0 text-slate-200" aria-hidden />} sm>
                        {t("editor.submit")}
                    </Button>
                )}
            </Toolbar>
        </Container>
    );
};
