/**
 * Editor toolbar: one Container with a Toolbar — mode buttons (Connect/Add/Erase/Move), trash, zoom.
 * Mode buttons are mutually exclusive; the active one gets the active prop.
 */
import { Minus, Trash2, Plus, Pen, PenLine, Hand, Eraser } from "lucide-react";
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
}

export const EditorToolbar = ({
    mode = EditorMode.Connect,
    onModeChange,
    onZoomOut,
    onClean,
    onZoomIn,
}: EditorToolbarProps) => {
    const { t } = useLocale();
    return (
        <Container name="geometry-editor-toolbar" middle center spaced>
            <Toolbar center>
                <Button
                    sm
                    active={mode === EditorMode.Connect}
                    icon={MODE_ICONS[EditorMode.Connect]}
                    onClick={() => onModeChange(EditorMode.Connect)}
                    aria-label={t("toolbar.tooltipConnect")}
                    tooltip={t("toolbar.tooltipConnect")}
                />
                <Button
                    sm
                    active={mode === EditorMode.Add}
                    icon={MODE_ICONS[EditorMode.Add]}
                    onClick={() => onModeChange(EditorMode.Add)}
                    aria-label={t("toolbar.tooltipAdd")}
                    tooltip={t("toolbar.tooltipAdd")}
                />
                <Button
                    sm
                    active={mode === EditorMode.Erase}
                    icon={MODE_ICONS[EditorMode.Erase]}
                    onClick={() => onModeChange(EditorMode.Erase)}
                    aria-label={t("toolbar.tooltipErase")}
                    tooltip={t("toolbar.tooltipErase")}
                />
                {onClean != null && (
                    <Button
                        sm
                        confirm={t("toolbar.clearConfirm")}
                        onClick={onClean}
                        icon={<Trash2 size={14} className="shrink-0" aria-hidden />}
                        aria-label={t("toolbar.tooltipClear")}
                        tooltip={t("toolbar.tooltipClear")}
                    />
                )}
                {onZoomOut != null && (
                    <Button
                        sm
                        onClick={onZoomOut}
                        icon={<Minus size={14} className="shrink-0" aria-hidden />}
                        aria-label={t("toolbar.tooltipZoomOut")}
                        tooltip={t("toolbar.tooltipZoomOut")}
                    />
                )}
                <Button
                    sm
                    active={mode === EditorMode.Move}
                    icon={MODE_ICONS[EditorMode.Move]}
                    onClick={() => onModeChange(EditorMode.Move)}
                    aria-label={t("toolbar.tooltipMove")}
                    tooltip={t("toolbar.tooltipMove")}
                />
                {onZoomIn != null && (
                    <Button
                        sm
                        onClick={onZoomIn}
                        icon={<Plus size={14} className="shrink-0" aria-hidden />}
                        aria-label={t("toolbar.tooltipZoomIn")}
                        tooltip={t("toolbar.tooltipZoomIn")}
                    />
                )}
            </Toolbar>
        </Container>
    );
};
