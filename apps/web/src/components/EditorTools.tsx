/**
 * Editor toolbar: Validate, Submit.
 */
import { useLocale } from "@geometry/i18n";
import { Toolbar, Button, Logo } from "@geometry/ui";

type EditorToolsProps = {
    disabled: boolean;
    onValidate: () => void;
    onSubmit: () => void;
};

export const EditorTools = ({ disabled, onValidate, onSubmit }: EditorToolsProps) => {
    const { t } = useLocale();
    return (
        <Toolbar left>
            <Button onClick={onValidate} disabled={disabled} icon={<Logo size={16} />}>
                {t("editor.validate")}
            </Button>
            <Button onClick={onSubmit} disabled={disabled} icon={<Logo size={16} />}>
                {t("editor.submit")}
            </Button>
        </Toolbar>
    );
};
