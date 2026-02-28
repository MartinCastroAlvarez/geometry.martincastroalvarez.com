/**
 * Editor toolbar: zoom out, clean (trash), zoom in.
 * Uses Container, Toolbar and Button from @geometry/ui and lucide-react icons.
 * Parent (Editor) positions this floating at bottom-right with margin and panel styling.
 */
import { Minus, Trash2, Plus } from "lucide-react";
import { Container, Toolbar, Button } from "@geometry/ui";

export interface EditorToolbarProps {
    onZoomOut: () => void;
    onClean: () => void;
    onZoomIn: () => void;
}

export const EditorToolbar = ({ onZoomOut, onClean, onZoomIn }: EditorToolbarProps) => (
    <Container name="geometry-editor-toolbar">
        <Toolbar right>
            <Button onClick={onZoomOut} icon={<Minus className="size-4 shrink-0 text-slate-200" aria-hidden />} aria-label="Zoom out" />
            <Button onClick={onClean} icon={<Trash2 className="size-4 shrink-0 text-slate-200" aria-hidden />} aria-label="Clear" />
            <Button onClick={onZoomIn} icon={<Plus className="size-4 shrink-0 text-slate-200" aria-hidden />} aria-label="Zoom in" />
        </Toolbar>
    </Container>
);
