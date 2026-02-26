import React from "react";
import { Container } from "./Container";
import { Button } from "./Button";
import { Text } from "./Text";

const Confirm: React.FC<{
    isOpen: boolean;
    message: string;
    onConfirm: () => void;
    onCancel: () => void;
}> = ({ isOpen, message, onConfirm, onCancel }) => {
    if (!isOpen) return null;
    return (
        <div className="geometry-confirm fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <Container name="geometry-confirm-dialog" padded rounded solid>
                <Container>
                    <Text>{message}</Text>
                </Container>
                <Container middle spaced right>
                    <Button onClick={onCancel} sm>
                        Cancel
                    </Button>
                    <Button onClick={onConfirm} sm>
                        Confirm
                    </Button>
                </Container>
            </Container>
        </div>
    );
};

export default Confirm;
