/**
 * Art gallery editor page: polygon boundary and obstacles.
 *
 * Context: Holds ArtGallery (perimeter + holes) in state; Editor from @geometry/editor
 * gets boundary and obstacles, reports changes via onChange. Toolbar has Validate and Submit;
 * Validate calls v1/polygon, Submit creates the job. Unrecoverable errors show in Problem above the toolbar (below the editor); validation results (200 with checks)
 * show in SummaryTable below the error.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArtGallery, Polygon } from "@geometry/domain";
import { Editor } from "@geometry/editor";
import { Container, Toolbar, Button, Problem, Input, Logo } from "@geometry/ui";
import { WithEditorPageSkeleton, SummaryTableSkeleton } from "../skeletons";
import { SummaryTable } from "../components/SummaryTable";
import { useSession, useValidatePolygon, useCreateJob } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { isValidationSuccess, type Summary } from "@geometry/domain";

const emptyGallery = new ArtGallery(new Polygon([]));

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

const getErrorMessage = (e: unknown): string | undefined =>
    e instanceof globalThis.Error ? e.message : e != null ? String(e) : undefined;

const TrashIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <polyline points="3 6 5 6 21 6" />
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        <line x1="10" y1="11" x2="10" y2="17" />
        <line x1="14" y1="11" x2="14" y2="17" />
    </svg>
);

export const EditorPage = () => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [editorSize, setEditorSize] = useState({ width: 850, height: 550 });
    const [gallery, setGallery] = useState<ArtGallery>(() => emptyGallery);
    const [validationResult, setValidationResult] = useState<Summary | null>(null);
    const [unrecoverableError, setUnrecoverableError] = useState<string | null>(null);
    const [galleryTitle, setGalleryTitle] = useState("");
    const [editorHasVertices, setEditorHasVertices] = useState(false);
    const { isLoading: sessionLoading } = useSession();
    const { t } = useLocale();
    const tipKey = useMemo(
        () => EDITOR_TIP_KEYS[Math.floor(Math.random() * EDITOR_TIP_KEYS.length)],
        []
    );
    const { track } = useAnalytics();
    const validatePolygon = useValidatePolygon();
    const createJob = useCreateJob();

    const mutationError =
        getErrorMessage(createJob.error) ?? getErrorMessage(validatePolygon.error);

    const rawError = mutationError ?? unrecoverableError;
    const errorMessage =
        rawError === "Failed to fetch"
            ? t("errors.failedToFetch")
            : rawError === "SERVICE_UNAVAILABLE"
              ? t("errors.serviceUnavailable")
              : (rawError ?? "");

    const hasContent =
        gallery.perimeter.points.length >= 1 ||
        gallery.holes.some((h) => h.points.length >= 1);
    const showToolbar = editorHasVertices || hasContent;

    useEffect(() => {
        if (mutationError) setUnrecoverableError(mutationError);
    }, [mutationError]);

    useEffect(() => {
        track({
            action: GoogleAnalyticsActions.EDITOR_OPEN,
            category: GoogleAnalyticsCategories.PAGE,
        });
    }, [track]);

    useEffect(() => {
        const el = editorRef.current;
        if (!el) return;
        const ro = new ResizeObserver((entries) => {
            const { width } = entries[0]?.contentRect ?? {};
            if (width != null && width > 0) {
                setEditorSize({ width, height: Math.round(width * 0.65) });
            }
        });
        ro.observe(el);
        return () => ro.disconnect();
    }, []);

    const boundaryPoints = gallery.perimeter.points.map((p) => ({ x: p.x, y: p.y }));
    const obstaclesPoints = gallery.holes.map((h) => h.points.map((p) => ({ x: p.x, y: p.y })));

    const handleValidate = useCallback(() => {
        setUnrecoverableError(null);
        setValidationResult(null);
        validatePolygon.mutate(
            { boundary: boundaryPoints, obstacles: obstaclesPoints },
            {
                onSuccess: (data) => {
                    setValidationResult(data);
                },
                onError: (err) => {
                    setUnrecoverableError(err instanceof globalThis.Error ? err.message : String(err));
                },
            }
        );
    }, [boundaryPoints, obstaclesPoints, validatePolygon]);

    const handleSubmit = useCallback(() => {
        setUnrecoverableError(null);
        const title = galleryTitle.trim() || t("editor.untitledGallery");
        createJob.mutate(
            { boundary: boundaryPoints, obstacles: obstaclesPoints, title },
            {
                onError: (err) => {
                    setUnrecoverableError(err instanceof globalThis.Error ? err.message : String(err));
                },
            }
        );
    }, [boundaryPoints, obstaclesPoints, galleryTitle, t, createJob]);

    const handleClean = useCallback(() => {
        setGallery(new ArtGallery(new Polygon([])));
        setEditorHasVertices(false);
        setValidationResult(null);
        setUnrecoverableError(null);
        validatePolygon.reset();
        createJob.reset();
    }, [validatePolygon, createJob]);

    const handleChange = useCallback(
        (boundary?: Polygon, obstacles?: Polygon[]) => {
            setGallery((prev) => {
                const perimeter = boundary ?? prev.perimeter;
                const holes = obstacles ?? prev.holes;
                return new ArtGallery(perimeter, holes, prev.guards);
            });
            setValidationResult(null);
            setUnrecoverableError(null);
        },
        []
    );

    return (
        <WithEditorPageSkeleton loading={sessionLoading}>
            <Container padded spaced size={12}>
                <Container padded spaced size={12} middle center>
                    <Input
                        type="text"
                        value={galleryTitle}
                        onChange={(e) => setGalleryTitle(e.target.value)}
                        placeholder={t("editor.untitledGallery")}
                        aria-label={t("editor.untitledGallery")}
                        className="max-w-md w-full"
                    />
                </Container>
                <Container ref={editorRef} name="geometry-editor-wrapper w-full max-h-[70vh]" size={12}>
                    <Editor
                        boundary={gallery.perimeter}
                        obstacles={gallery.holes}
                        width={editorSize.width}
                        height={editorSize.height}
                        onChange={handleChange}
                        onVerticesChange={setEditorHasVertices}
                    />
                </Container>
                <Container padded spaced size={12}>
                    <p
                        className="w-full text-sm text-white/60 font-normal leading-relaxed"
                        style={{ textAlign: "center" }}
                    >
                        {t(tipKey)}
                    </p>
                </Container>
                {showToolbar && (
                <Container padded spaced size={12}>
                    <Toolbar>
                        <Button
                            onClick={handleClean}
                            disabled={validatePolygon.isPending || createJob.isPending}
                            icon={<TrashIcon />}
                            aria-label={t("toolbar.clear")}
                        >
                            {t("toolbar.clear")}
                        </Button>
                        <Button
                            onClick={handleValidate}
                            disabled={validatePolygon.isPending || createJob.isPending}
                            icon={<Logo size={16} />}
                        >
                            {t("editor.validate")}
                        </Button>
                        {validationResult && isValidationSuccess(validationResult) && (
                            <Button
                                onClick={handleSubmit}
                                disabled={validatePolygon.isPending || createJob.isPending}
                                icon={<Logo size={16} />}
                            >
                                {t("editor.submit")}
                            </Button>
                        )}
                    </Toolbar>
                </Container>
                )}
                <Container padded spaced size={12}>
                    <Problem>{errorMessage}</Problem>
                </Container>
            {validatePolygon.isPending && <SummaryTableSkeleton />}
            {validationResult && !validatePolygon.isPending && (
                <SummaryTable summary={validationResult} />
            )}
            </Container>
        </WithEditorPageSkeleton>
    );
};
