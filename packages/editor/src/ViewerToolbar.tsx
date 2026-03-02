/**
 * Viewer toolbar: mode buttons in order — polygon, stitch, ear clipping, convex, guard visibility.
 * One mode is active at a time; active button gets the active prop.
 */
import { TriangleDashed, Hexagon, SquareDashed, Waypoints, Eye } from "lucide-react";
import { Container, Toolbar, Button } from "@geometry/ui";
import { useLocale } from "@geometry/i18n";
import { ViewerMode } from "./ViewerMode";

const MODE_ICONS: Record<ViewerMode, React.ReactNode> = {
    [ViewerMode.Default]: <Hexagon size={14} className="shrink-0" aria-hidden />,
    [ViewerMode.EarClipping]: <TriangleDashed size={14} className="shrink-0" aria-hidden />,
    [ViewerMode.ConvexComponent]: <SquareDashed size={14} className="shrink-0" aria-hidden />,
    [ViewerMode.Stitching]: <Waypoints size={14} className="shrink-0" aria-hidden />,
    [ViewerMode.Visibility]: <Eye size={14} className="shrink-0" aria-hidden />,
};

export interface ViewerToolbarProps {
    mode: ViewerMode;
    onModeChange: (mode: ViewerMode) => void;
    /** When true, align buttons to the right; when false, center. Default false (e.g. for mobile). */
    alignRight?: boolean;
}

export const ViewerToolbar = ({ mode, onModeChange, alignRight = false }: ViewerToolbarProps) => {
    const { t } = useLocale();
    return (
        <Container name="geometry-viewer-toolbar" middle center={!alignRight} right={alignRight} spaced>
            <Toolbar center={!alignRight} right={alignRight}>
                <Button
                    sm
                    active={mode === ViewerMode.Default}
                    icon={MODE_ICONS[ViewerMode.Default]}
                    onClick={() => onModeChange(ViewerMode.Default)}
                    aria-label={t("toolbar.tooltipViewerDefault")}
                    tooltip={t("toolbar.tooltipViewerDefault")}
                />
                <Button
                    sm
                    active={mode === ViewerMode.Stitching}
                    icon={MODE_ICONS[ViewerMode.Stitching]}
                    onClick={() => onModeChange(ViewerMode.Stitching)}
                    aria-label={t("toolbar.tooltipViewerStitching")}
                    tooltip={t("toolbar.tooltipViewerStitching")}
                />
                <Button
                    sm
                    active={mode === ViewerMode.EarClipping}
                    icon={MODE_ICONS[ViewerMode.EarClipping]}
                    onClick={() => onModeChange(ViewerMode.EarClipping)}
                    aria-label={t("toolbar.tooltipViewerEarClipping")}
                    tooltip={t("toolbar.tooltipViewerEarClipping")}
                />
                <Button
                    sm
                    active={mode === ViewerMode.ConvexComponent}
                    icon={MODE_ICONS[ViewerMode.ConvexComponent]}
                    onClick={() => onModeChange(ViewerMode.ConvexComponent)}
                    aria-label={t("toolbar.tooltipViewerConvexComponent")}
                    tooltip={t("toolbar.tooltipViewerConvexComponent")}
                />
                <Button
                    sm
                    active={mode === ViewerMode.Visibility}
                    icon={MODE_ICONS[ViewerMode.Visibility]}
                    onClick={() => onModeChange(ViewerMode.Visibility)}
                    aria-label={t("toolbar.tooltipViewerVisibility")}
                    tooltip={t("toolbar.tooltipViewerVisibility")}
                />
            </Toolbar>
        </Container>
    );
};
