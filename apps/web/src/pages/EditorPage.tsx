/**
 * Art gallery editor page: polygon boundary and obstacles.
 *
 * Context: This is the main design surface where users draw and edit art gallery polygons. It holds
 * an ArtGallery (boundary polygon + obstacle polygons) in React state and passes it
 * to the Editor from @geometry/editor, which reports geometry changes via onChange. The layout is
 * responsive: on desktop the editor and summary sit side-by-side (e.g. 8/4 columns); on mobile they
 * stack. The editor size is driven by a ResizeObserver on the wrapper so it scales with the viewport.
 *
 * Users can set an optional title (synced to job meta on submit). The toolbar shows Validate and
 * Submit: Validate calls the v1/polygon API and displays the returned Summary in the summary panel
 * (success/error badges and notes); Submit runs validation and on success creates a job via
 * useCreateJob, then the app can navigate to the job.
 *
 * Unrecoverable errors (network, 4xx/5xx, or validation failure messages) are shown in EditorReview
 * below the Validate/Submit buttons. While validation or create is pending, a skeleton replaces the summary
 * table. EditorReview shows a skeleton when loading, else validation results or the requirement list.
 * A random tip is shown at the bottom. Session is required (skeleton while useSession loads). Analytics: EDITOR_OPEN on mount.
 */
import { useCallback, useEffect, useRef, useState, startTransition } from "react";
import { ArtGallery, Polygon } from "@geometry/domain";
import { Editor, EditorReview } from "@geometry/editor";
import { Container, Input, useDevice } from "@geometry/ui";
import { WithEditorPageSkeleton } from "../skeletons";
import { useSession, useValidateJob, useCreateJob, validateJob } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { isValidationSuccess, type Summary } from "@geometry/domain";

const EDITOR_COL_DESKTOP = 8;
const SUMMARY_COL_DESKTOP = 4;
const EDITOR_INITIAL_WIDTH = 850;
const EDITOR_INITIAL_HEIGHT = 550;
const EDITOR_ASPECT_RATIO = 0.65;

const emptyGallery = new ArtGallery(new Polygon([]));

export const EditorPage = () => {
    const { isMobile } = useDevice();
    const editorRef = useRef<HTMLDivElement>(null);
    const [editorSize, setEditorSize] = useState({ width: EDITOR_INITIAL_WIDTH, height: EDITOR_INITIAL_HEIGHT });
    const [gallery, setGallery] = useState<ArtGallery>(() => emptyGallery);
    const [validationResult, setValidationResult] = useState<Summary | null>(null);
    const [galleryTitle, setGalleryTitle] = useState("");
    const { isLoading: sessionLoading } = useSession();
    const { t } = useLocale();
    const { track } = useAnalytics();
    const validateJobMutation = useValidateJob();
    const createJob = useCreateJob();

    const unrecoverableError =
        createJob.error ?? validateJobMutation.error;

    /** Prefer a short, user-facing message; hide raw technical errors (e.g. unserialize, stack traces). */
    const errorMessage = (() => {
        if (unrecoverableError == null) return null;
        const raw =
            unrecoverableError instanceof Error
                ? unrecoverableError.message
                : String(unrecoverableError);
        const looksTechnical =
            /unserialize|deserializ|expected|list of|objects|decimals|str|ION\)/i.test(raw) ||
            raw.length > 120;
        if (looksTechnical) {
            if (validateJobMutation.error != null) return t("editor.errorValidation");
            if (createJob.error != null) return t("editor.errorSubmit");
            return t("editor.errorGeneric");
        }
        return raw;
    })();

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
        validateJobMutation.reset();
        createJob.reset();
        setValidationResult(null);
        validateJobMutation.mutate(gallery, { onSuccess: (data) => setValidationResult(data) });
    }, [gallery, validateJobMutation, createJob]);

    const handleSubmit = useCallback(() => {
        validateJobMutation.reset();
        createJob.reset();
        setValidationResult(null);
        validateJobMutation.mutate(gallery, {
            onSuccess: (data) => {
                setValidationResult(data);
                if (isValidationSuccess(data)) {
                    const title = galleryTitle.trim() || t("editor.untitledGallery");
                    const { boundary, obstacles } = validateJob(gallery);
                    createJob.mutate({ boundary, obstacles, title });
                }
            },
        });
    }, [gallery, galleryTitle, t, validateJobMutation, createJob]);

    const handleChange = useCallback(
        (next: ArtGallery | null) => {
            startTransition(() => {
                setGallery(next ?? emptyGallery);
                setValidationResult(null);
                validateJobMutation.reset();
                createJob.reset();
            });
        },
        [validateJobMutation, createJob]
    );

    return (
        <WithEditorPageSkeleton loading={sessionLoading}>
            <Container padded spaced>
                <Container>
                    <Container {...(!isMobile && { size: EDITOR_COL_DESKTOP })}>
                        <Container middle center>
                            <Input
                                type="text"
                                value={galleryTitle}
                                onChange={(e) => setGalleryTitle(e.target.value)}
                                placeholder={t("editor.untitledGallery")}
                                aria-label={t("editor.untitledGallery")}
                                className="max-w-md w-full"
                                lg
                                transparent
                            />
                        </Container>
                        <Container>
                        <div
                            ref={editorRef}
                            style={{ display: "grid", width: "100%", minHeight: EDITOR_INITIAL_HEIGHT }}
                        >
                            <Editor
                                width={editorSize.width}
                                height={editorSize.height}
                                gallery={gallery}
                                onChange={handleChange}
                            />
                        </div>
                        </Container>
                    </Container>
                    <Container padded spaced left {...(!isMobile && { size: SUMMARY_COL_DESKTOP })}>
                        <Container size={isMobile ? 0 : 12}>
                            <br />
                        </Container>
                        <div className="col-span-12 w-full min-w-0">
                            <EditorReview
                                summary={validationResult ?? undefined}
                                artGallery={gallery}
                                errorMessage={errorMessage}
                                isLoading={validateJobMutation.isPending}
                                onValidate={handleValidate}
                                onSubmit={handleSubmit}
                                disabled={validateJobMutation.isPending || createJob.isPending}
                            />
                        </div>
                    </Container>
                </Container>
            </Container>
        </WithEditorPageSkeleton>
    );
};
