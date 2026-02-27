/**
 * Editor toolbar: vertex count, closed state, and actions (undo, start hole, close polygon, clear).
 *
 * Context: Uses @geometry/ui (Container, Button, Text, Buttons) and @geometry/i18n useLocale for labels.
 * Callbacks (onUndo, onStartHole, onClosePolygon, onClear) are invoked by the parent; disabled states depend on vertexCount, isClosed, isAddingHole.
 *
 * Example:
 *   <Toolbar vertexCount={5} isClosed isAddingHole={false} onUndo={...} onStartHole={...} onClosePolygon={...} onClear={...} />
 */

import { Container, Button, Text, Buttons } from "@geometry/ui";
import { useLocale } from "@geometry/i18n";
import { Undo, Target, Check, Trash2 } from "lucide-react";

export interface ToolbarProps {
    vertexCount: number;
    isClosed: boolean;
    isAddingHole: boolean;
    onUndo: () => void;
    onStartHole: () => void;
    onClosePolygon: () => void;
    onClear: () => void;
    readonly?: boolean;
}

export const Toolbar = ({
    vertexCount,
    isClosed,
    isAddingHole,
    onUndo,
    onStartHole,
    onClosePolygon,
    onClear,
    readonly = false,
}: ToolbarProps) => {
    const { t } = useLocale();
    return (
        <Container solid padded spaced rounded>
            <Container middle spaced size={12}>
                <Container size={4} left middle>
                    <Text sm>{vertexCount} {t("toolbar.vertices")}</Text>
                    {isClosed ? (
                        <Container middle spaced left>
                            <Check size={14} />
                            <Text sm>{t("toolbar.closed")}</Text>
                        </Container>
                    ) : vertexCount >= 3 ? (
                        <Text sm>{t("toolbar.open")}</Text>
                    ) : null}
                </Container>
                {!readonly && (
                    <Container size={8} right middle>
                        <Buttons right>
                        <Button
                            onClick={onUndo}
                            disabled={vertexCount === 0 && !isAddingHole}
                            sm
                            icon={<Undo size={14} />}
                        >
                            {t("toolbar.undo")}
                        </Button>
                        <Button
                            onClick={onStartHole}
                            disabled={!isClosed || isAddingHole}
                            sm
                            icon={<Target size={14} />}
                        >
                            {t("toolbar.hole")}
                        </Button>
                        <Button
                            onClick={onClosePolygon}
                            disabled={isClosed || vertexCount < 3}
                            sm
                            icon={<Check size={14} />}
                        >
                            {t("toolbar.close")}
                        </Button>
                        <Button onClick={onClear} sm confirm={t("toolbar.clearConfirm")} icon={<Trash2 size={14} />}>
                            {t("toolbar.clear")}
                        </Button>
                        </Buttons>
                    </Container>
                )}
            </Container>
            {!readonly && !isClosed && vertexCount > 0 && (
                <Container center>
                    <Text xs center>
                        {vertexCount < 3
                            ? t(3 - vertexCount > 1 ? "toolbar.addVerticesPlural" : "toolbar.addVertices", { count: 3 - vertexCount })
                            : t("toolbar.clickToClose")}
                    </Text>
                </Container>
            )}
        </Container>
    );
};
