/**
 * Art gallery editor page: polygon boundary and obstacles.
 *
 * Context: This is the main design surface where users draw and edit art gallery polygons. It holds
 * an ArtGallery (perimeter polygon + hole polygons) in React state and passes boundary and obstacles
 * to the Editor from @geometry/editor, which reports geometry changes via onChange. The layout is
 * responsive: on desktop the editor and summary sit side-by-side (e.g. 8/4 columns); on mobile they
 * stack. The editor size is driven by a ResizeObserver on the wrapper so it scales with the viewport.
 *
 * Users can set an optional title (synced to job meta on submit). The toolbar shows Validate and
 * Submit: Validate calls the v1/polygon API and displays the returned Summary in the summary panel
 * (success/error badges and notes); Submit runs validation and on success creates a job via
 * useCreateJob, then the app can navigate to the job.
 *
 * Unrecoverable errors (network, 4xx/5xx, or validation failure messages) are shown in a Problem
 * block above the toolbar. While validation or create is pending, a skeleton replaces the summary
 * table. The summary panel otherwise shows either EditorSummaryTable (validation results) or, when
 * there is no summary, the same component falls back to EditorInfoTable (requirement bullets).
 * EditorRecommendation at the bottom displays a random tip. Session is required (skeleton while
 * useSession loads). Analytics: EDITOR_OPEN on mount.
 */
import { useCallback, useEffect, useRef, useState, startTransition } from "react";
import { ArtGallery, Polygon } from "@geometry/domain";
import { Editor } from "@geometry/editor";
import { Container, Problem, Input, useDevice } from "@geometry/ui";
import { WithEditorPageSkeleton, SummaryTableSkeleton } from "../skeletons";
import { EditorSummaryTable } from "../components/EditorSummaryTable";
import { EditorRecommendation } from "../components/EditorRecommendation";
import { useSession, useValidatePolygon, useCreateJob } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { isValidationSuccess, type Summary } from "@geometry/domain";

const EDITOR_COL_DESKTOP = 8;
const SUMMARY_COL_DESKTOP = 4;
const EDITOR_INITIAL_WIDTH = 850;
const EDITOR_INITIAL_HEIGHT = 550;
const EDITOR_ASPECT_RATIO = 0.65;

const emptyGallery = new ArtGallery(new Polygon([]));

const getErrorMessage = (e: unknown): string | undefined =>
    e instanceof globalThis.Error ? e.message : e != null ? String(e) : undefined;

export const EditorPage = () => {
    const { isMobile } = useDevice();
    const editorRef = useRef<HTMLDivElement>(null);
    const [editorSize, setEditorSize] = useState({ width: EDITOR_INITIAL_WIDTH, height: EDITOR_INITIAL_HEIGHT });
    const [gallery, setGallery] = useState<ArtGallery>(() => emptyGallery);
    const [validationResult, setValidationResult] = useState<Summary | null>(null);
    const [unrecoverableError, setUnrecoverableError] = useState<string | null>(null);
    const [galleryTitle, setGalleryTitle] = useState("");
    const { isLoading: sessionLoading } = useSession();
    const { t } = useLocale();
    const { track } = useAnalytics();
    const validatePolygon = useValidatePolygon();
    const createJob = useCreateJob();

    const mutationError =
        getErrorMessage(createJob.error) ?? getErrorMessage(validatePolygon.error);

    const errorMessage = (() => {
        const r = mutationError ?? unrecoverableError;
        return r === "Failed to fetch"
            ? t("errors.failedToFetch")
            : r === "SERVICE_UNAVAILABLE"
              ? t("errors.serviceUnavailable")
              : (r ?? "");
    })();

    const boundaryPoints = gallery.perimeter.toDict().points;
    const obstaclesPoints = gallery.holes.map((h) => h.toDict().points);

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
                setEditorSize({ width, height: Math.round(width * EDITOR_ASPECT_RATIO) });
            }
        });
        ro.observe(el);
        return () => ro.disconnect();
    }, []);

    const handleValidate = useCallback(() => {
        setUnrecoverableError(null);
        setValidationResult(null);
        validatePolygon.mutate(
            { boundary: boundaryPoints, obstacles: obstaclesPoints },
            {
                onSuccess: (data) => setValidationResult(data),
                onError: (err) => {
                    setUnrecoverableError(err instanceof globalThis.Error ? err.message : String(err));
                },
            }
        );
    }, [boundaryPoints, obstaclesPoints, validatePolygon]);

    const handleSubmit = useCallback(() => {
        setUnrecoverableError(null);
        setValidationResult(null);
        validatePolygon.mutate(
            { boundary: boundaryPoints, obstacles: obstaclesPoints },
            {
                onSuccess: (data) => {
                    setValidationResult(data);
                    if (isValidationSuccess(data)) {
                        const title = galleryTitle.trim() || t("editor.untitledGallery");
                        createJob.mutate(
                            { boundary: boundaryPoints, obstacles: obstaclesPoints, title },
                            {
                                onError: (err) => {
                                    setUnrecoverableError(err instanceof globalThis.Error ? err.message : String(err));
                                },
                            }
                        );
                    }
                },
                onError: (err) => {
                    setUnrecoverableError(err instanceof globalThis.Error ? err.message : String(err));
                },
            }
        );
    }, [boundaryPoints, obstaclesPoints, galleryTitle, t, validatePolygon, createJob]);

    const handleChange = useCallback(
        (boundary?: Polygon, obstacles?: Polygon[]) => {
            startTransition(() => {
                setGallery((prev) => {
                    const perimeter = boundary ?? prev.perimeter;
                    const holes = obstacles ?? prev.holes;
                    return new ArtGallery(perimeter, holes, prev.guards);
                });
                setValidationResult(null);
                setUnrecoverableError(null);
            });
        },
        []
    );

    const handleClean = useCallback(() => {
        setGallery(emptyGallery);
        setValidationResult(null);
        setUnrecoverableError(null);
        validatePolygon.reset();
        createJob.reset();
    }, [validatePolygon, createJob]);

    return (
        <WithEditorPageSkeleton loading={sessionLoading}>
            <Container padded spaced>
                <Container padded spaced middle center>
                    <Input
                        type="text"
                        value={galleryTitle}
                        onChange={(e) => setGalleryTitle(e.target.value)}
                        placeholder={t("editor.untitledGallery")}
                        aria-label={t("editor.untitledGallery")}
                        className="max-w-md w-full"
                    />
                </Container>
                <Container>
                    <Container padded ref={editorRef} name="geometry-editor-wrapper w-full h-[70vh] min-h-[400px] relative" {...(!isMobile && { size: EDITOR_COL_DESKTOP })}>
                        <Editor
                            width={editorSize.width}
                            height={editorSize.height}
                            onChange={handleChange}
                            onZoomOut={() => {}}
                            onClean={handleClean}
                            onZoomIn={() => {}}
                            onValidate={handleValidate}
                            onSubmit={handleSubmit}
                            disabled={validatePolygon.isPending || createJob.isPending}
                        />
                    </Container>
                    <Container padded spaced left {...(!isMobile && { size: SUMMARY_COL_DESKTOP })}>
                        {errorMessage && <Problem>{errorMessage}</Problem>}
                        {validatePolygon.isPending && <SummaryTableSkeleton variant="results" />}
                        {!validatePolygon.isPending && <EditorSummaryTable summary={validationResult ?? undefined} />}
                    </Container>
                </Container>
                <EditorRecommendation />
            </Container>
        </WithEditorPageSkeleton>
    );
};
