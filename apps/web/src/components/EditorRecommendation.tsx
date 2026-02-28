/**
 * Editor recommendation: random tip message below the editor.
 *
 * Context: Picks one tip from a fixed list (EDITOR_TIP_KEYS) at mount via useMemo and displays it
 * in a centered, padded container. Tips cover editor actions: click to add, double-click hole,
 * split edge, connect vertices, boundary rules, drag, delete key, arrow scroll, validate then submit.
 * No props; purely presentational. Uses @geometry/i18n for the translated message.
 *
 * Example:
 *   <EditorRecommendation />
 */
import { useMemo } from "react";
import { useLocale } from "@geometry/i18n";
import { Container, Text } from "@geometry/ui";

const EDITOR_TIP_KEYS = [
    "editor.tips.clickToAdd",
    "editor.tips.doubleClickHole",
    "editor.tips.clickEdgeToSplit",
    "editor.tips.connectTwoVertices",
    "editor.tips.largestIsBoundary",
    "editor.tips.dragVertices",
    "editor.tips.deleteKey",
    "editor.tips.arrowKeysScroll",
    "editor.tips.validateThenSubmit",
] as const;

export const EditorRecommendation = () => {
    const { t } = useLocale();
    const message = useMemo(
        () => EDITOR_TIP_KEYS[Math.floor(Math.random() * EDITOR_TIP_KEYS.length)],
        []
    );
    return (
        <Container padded spaced center middle>
            <Text sm center muted>{t(message)}</Text>
        </Container>
    );
};
