/**
 * Modal confirm dialog: overlay with title, message and Confirm/Cancel buttons.
 *
 * Context: When isOpen is true, renders a fixed full-screen overlay (backdrop blur) and a
 * dialog with Title, message (Text), and Toolbar with Cancel/Confirm Buttons. Uses
 * common.confirmTitle for the title; message is passed in (already localized by caller).
 * Used by Button when confirm prop is set.
 *
 * Example:
 *   <Confirm isOpen={open} message={t("toolbar.clearConfirm")} onConfirm={handleDelete} onCancel={() => setOpen(false)} />
 */

import React from "react";
import { Container } from "./Container";
import { Button, Toolbar } from "./Button";
import { Text } from "./Text";
import { Title } from "./Title";
import { useLocale } from "@geometry/i18n";

const Confirm: React.FC<{
    isOpen: boolean;
    message: string;
    onConfirm: () => void;
    onCancel: () => void;
}> = ({ isOpen, message, onConfirm, onCancel }) => {
    const { t } = useLocale();
    if (!isOpen) return null;
    return (
        <div
            className="geometry-confirm fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-sm"
            onClick={onCancel}
        >
            <Container
                name="geometry-confirm-dialog"
                padded
                rounded
                solid
                className="w-full max-w-md"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex flex-col gap-4">
                    <Container>
                        <Title lg>{t("common.confirmTitle")}</Title>
                    </Container>
                    <Container>
                        <Text sm center>{message}</Text>
                    </Container>
                    <Toolbar center>
                        <Button onClick={onConfirm} sm primary>
                            {t("common.confirm")}
                        </Button>
                        <Button onClick={onCancel} sm>
                            {t("common.cancel")}
                        </Button>
                    </Toolbar>
                </div>
            </Container>
        </div>
    );
};

export default Confirm;
