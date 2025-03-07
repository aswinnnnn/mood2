export interface UserData {
    username: string;
    email: string;
    password: string;
    name: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user_id: string;
}

export interface LoginCredentials {
    username: string;
    password: string;
} 