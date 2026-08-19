import {
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  type User,
} from "firebase/auth"

import {
  useEffect,
  useState,
  type ReactNode,
} from "react"

import {
  auth,
  googleProvider,
} from "./firebase"

import "./AuthGate.css"

type AuthState =
  | "loading"
  | "signed-out"
  | "checking"
  | "authorized"
  | "forbidden"
  | "error"

type AuthMe = {
  uid: string
  email: string
}

async function verifyBackendUser(
  user: User,
): Promise<AuthMe> {
  const token =
    await user.getIdToken()

  const response =
    await fetch(
      "/api/auth/me",
      {
        headers: {
          Authorization:
            `Bearer ${token}`,
        },
      },
    )

  if (response.status === 403) {
    throw new Error(
      "SMARTVITRA_FORBIDDEN",
    )
  }

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status}`,
    )
  }

  return response.json() as Promise<AuthMe>
}

function AuthGate({
  children,
}: {
  children: ReactNode
}) {
  const [state, setState] =
    useState<AuthState>("loading")

  const [user, setUser] =
    useState<User | null>(null)

  const [email, setEmail] =
    useState<string | null>(null)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    return onAuthStateChanged(
      auth,
      async (currentUser) => {
        setUser(currentUser)
        setError(null)

        if (!currentUser) {
          setEmail(null)
          setState("signed-out")
          return
        }

        setState("checking")

        try {
          const me =
            await verifyBackendUser(
              currentUser,
            )

          setEmail(me.email)
          setState("authorized")
        } catch (err) {
          if (
            err instanceof Error &&
            err.message ===
              "SMARTVITRA_FORBIDDEN"
          ) {
            setEmail(
              currentUser.email,
            )
            setState("forbidden")
            return
          }

          setError(
            err instanceof Error
              ? err.message
              : "Error de autenticación",
          )

          setState("error")
        }
      },
    )
  }, [])

  async function login() {
    try {
      setError(null)

      await signInWithPopup(
        auth,
        googleProvider,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo iniciar sesión",
      )
    }
  }

  async function logout() {
    await signOut(auth)

    setUser(null)
    setEmail(null)
    setState("signed-out")
  }

  if (
    state === "loading" ||
    state === "checking"
  ) {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div className="auth-brand">
            SmartVitra
          </div>

          <p>
            Verificando acceso…
          </p>
        </section>
      </main>
    )
  }

  if (state === "signed-out") {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div className="auth-brand">
            SmartVitra
          </div>

          <h1>
            Acceso a SmartVitra
          </h1>

          <p>
            Inicia sesión con la cuenta
            de Google autorizada.
          </p>

          <button
            className="auth-button"
            onClick={login}
          >
            Continuar con Google
          </button>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}
        </section>
      </main>
    )
  }

  if (state === "forbidden") {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div className="auth-brand">
            SmartVitra
          </div>

          <h1>
            Acceso no autorizado
          </h1>

          <p>
            La cuenta
            {" "}
            <strong>
              {email ?? "actual"}
            </strong>
            {" "}
            no tiene acceso a
            SmartVitra.
          </p>

          <button
            className="auth-button"
            onClick={logout}
          >
            Usar otra cuenta
          </button>
        </section>
      </main>
    )
  }

  if (state === "error") {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div className="auth-brand">
            SmartVitra
          </div>

          <h1>
            Error de acceso
          </h1>

          <p>
            {error ??
              "No se pudo verificar la sesión."}
          </p>

          <button
            className="auth-button"
            onClick={logout}
          >
            Volver a iniciar sesión
          </button>
        </section>
      </main>
    )
  }

  if (
    state === "authorized" &&
    user
  ) {
    return (
      <>
        <div className="auth-session">
          <span>
            {email}
          </span>

          <button
            onClick={logout}
          >
            Cerrar sesión
          </button>
        </div>

        {children}
      </>
    )
  }

  return null
}

export default AuthGate
