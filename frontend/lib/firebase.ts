import { getApps, initializeApp, type FirebaseApp } from "firebase/app";
import { getAuth, signInAnonymously, type Auth } from "firebase/auth";

const config = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

export const firebaseEnabled = Boolean(config.apiKey && config.projectId);

let app: FirebaseApp | null = null;

export function getFirebaseAuth(): Auth | null {
  if (!firebaseEnabled) return null;
  app ??= getApps()[0] ?? initializeApp(config);
  return getAuth(app);
}

export async function signInAsGuest() {
  const auth = getFirebaseAuth();
  if (!auth) return null;
  return (await signInAnonymously(auth)).user;
}
