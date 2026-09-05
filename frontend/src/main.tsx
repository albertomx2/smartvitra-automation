import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import App from "./App.tsx"
import AuthGate from "./AuthGate.tsx"
import FatalErrorBoundary from "./FatalErrorBoundary.tsx"

import "./index.css"

const rootElement =
  document.getElementById("root")

const fatalRoot =
  document.getElementById("fatal-root")

function showFatalFallback(
  error: unknown,
) {
  console.error(
    "Error no recuperable en SmartVitra",
    error,
  )

  if (!fatalRoot) {
    return
  }

  fatalRoot.replaceChildren()

  const page =
    document.createElement("main")
  page.className =
    "fatal-error-page notranslate"
  page.translate = false

  const card =
    document.createElement("section")
  card.className = "fatal-error-card"

  const title =
    document.createElement("h1")
  title.textContent =
    "No se pudo mostrar la aplicación"

  const message =
    document.createElement("p")
  message.textContent =
    "Recarga la página para continuar. Si el problema persiste, desactiva la traducción automática para este sitio."

  const reloadButton =
    document.createElement("button")
  reloadButton.type = "button"
  reloadButton.textContent =
    "Recargar SmartVitra"
  reloadButton.addEventListener(
    "click",
    () => window.location.reload(),
  )

  card.append(
    title,
    message,
    reloadButton,
  )
  page.append(card)
  fatalRoot.append(page)
}

if (!rootElement) {
  throw new Error(
    "No se encontró el contenedor raíz",
  )
}

createRoot(rootElement, {
  onUncaughtError: showFatalFallback,
}).render(
  <StrictMode>
    <FatalErrorBoundary>
      <AuthGate>
        <App />
      </AuthGate>
    </FatalErrorBoundary>
  </StrictMode>,
)
