import { initializeApp } from "firebase/app"
import {
  GoogleAuthProvider,
  getAuth,
} from "firebase/auth"

const firebaseConfig = {
  apiKey:
    "AIzaSyC1JK_krOLXe5QpxRr8L_I-kBZ1a12Jg-A",
  authDomain:
    "project-c165bbbb-9f62-48fc-ba9.firebaseapp.com",
}

const firebaseApp =
  initializeApp(firebaseConfig)

export const auth =
  getAuth(firebaseApp)

export const googleProvider =
  new GoogleAuthProvider()
