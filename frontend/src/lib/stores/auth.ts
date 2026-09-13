import { writable } from "svelte/store";

export interface User {
  id: string;
  nombre: string;
  email: string;
  rol: string;
}

export interface ApiError {
  detail: {
    code: string;
    message: string;
  };
}

function createAuthStore() {
  const { subscribe, set } = writable<User | null>(null);

  return {
    subscribe,
    setUser: (user: User | null) => set(user),
    logout: () => set(null),
  };
}

export const auth = createAuthStore();
