/**
 * User and UserDict: authenticated user identity and serialization.
 *
 * Context: User is built from session/API dict (email, name, avatarUrl). fromDict/toDict for transport.
 * Used by auth/session layer; nullables for optional profile fields.
 *
 * Example:
 *   const user = User.fromDict({ email: 'a@b.com', name: 'A', avatarUrl: null });
 *   user.toDict();  // { email, name, avatarUrl }
 */
export interface UserDict {
    email: string | null;
    name: string | null;
    avatarUrl: string | null;
}

export class User {
    constructor(
        public readonly email: string | null,
        public readonly name: string | null,
        public readonly avatarUrl: string | null,
    ) {}

    static fromDict(dict: UserDict): User {
        return new User(
            dict.email ?? null,
            dict.name ?? null,
            dict.avatarUrl ?? null,
        );
    }

    toDict(): UserDict {
        return {
            email: this.email,
            name: this.name,
            avatarUrl: this.avatarUrl,
        };
    }
}
