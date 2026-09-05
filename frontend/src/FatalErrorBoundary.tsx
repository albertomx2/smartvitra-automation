import {
  Component,
  type ErrorInfo,
  type ReactNode,
} from "react"

import "./FatalErrorBoundary.css"

type Props = {
  children: ReactNode
}

type State = {
  failed: boolean
}

class FatalErrorBoundary extends Component<
  Props,
  State
> {
  state: State = {
    failed: false,
  }

  static getDerivedStateFromError(): State {
    return {
      failed: true,
    }
  }

  componentDidCatch(
    error: unknown,
    errorInfo: ErrorInfo,
  ) {
    console.error(
      "Error inesperado en SmartVitra",
      error,
      errorInfo,
    )
  }

  render() {
    if (this.state.failed) {
      return (
        <main
          className="fatal-error-page notranslate"
          translate="no"
        >
          <section className="fatal-error-card">
            <div className="fatal-error-brand">
              SmartVitra
            </div>

            <h1>
              No se pudo mostrar la aplicación
            </h1>

            <p>
              Recarga la página para continuar. Si el
              problema persiste, desactiva la traducción
              automática para este sitio.
            </p>

            <button
              type="button"
              onClick={() => window.location.reload()}
            >
              Recargar SmartVitra
            </button>
          </section>
        </main>
      )
    }

    return this.props.children
  }
}

export default FatalErrorBoundary
