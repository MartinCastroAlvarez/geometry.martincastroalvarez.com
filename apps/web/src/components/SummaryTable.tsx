/**
 * Validation summary table: list of check rows with badge (status) and note.
 * Receives the validation API output (Summary) and renders it below the editor toolbar.
 */
import type { Summary } from "@geometry/domain";
import { Container, Badge } from "@geometry/ui";

function summaryRows(summary: Summary): { key: string; status: string; note: string }[] {
    const statusKeys = Object.keys(summary).filter((k) => !k.endsWith(".note"));
    return statusKeys
        .sort()
        .map((key) => {
            const status = summary[key] ?? "pending";
            const note = summary[`${key}.note`] ?? "";
            return { key, status: status === "failed" ? "ERROR" : status.toUpperCase(), note };
        });
}

export interface SummaryTableProps {
    summary: Summary;
}

export const SummaryTable = ({ summary }: SummaryTableProps) => {
    const rows = summaryRows(summary);
    if (rows.length === 0) return null;

    return (
        <Container padded spaced rounded solid size={12}>
            {rows.map(({ key, status, note }) => (
                <Container key={key} size={12} spaced left middle>
                    <Container size={3} left middle>
                        <Badge danger={status === "ERROR"} success={status === "SUCCESS"}>
                            {status}
                        </Badge>
                    </Container>
                    <Container size={9} left middle>
                        {note}
                    </Container>
                </Container>
            ))}
        </Container>
    );
};
