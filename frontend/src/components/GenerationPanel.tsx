import {
  useEffect,
  useState,
} from "react"

import {
  createGenerationJob,
  getGenerationJob,
} from "../api/client"

import type {
  GenerationJob,
} from "../api/types"

interface GenerationPanelProps {
  caseId: string
}

const STEPS = [
  {
    key: "snapshotting",
    label: "Recopilando presupuesto",
  },
  {
    key: "building_context",
    label: "Preparando información",
  },
  {
    key: "generating_content",
    label: "Generando contenido",
  },
  {
    key: "rendering_presentation",
    label: "Preparando presentación",
  },
  {
    key: "saving_output",
    label: "Guardando presentación",
  },
]

function stepIndex(
  step: string | null,
): number {
  if (!step) {
    return -1
  }

  return STEPS.findIndex(
    (candidate) =>
      candidate.key === step,
  )
}

export default function GenerationPanel({
  caseId,
}: GenerationPanelProps) {
  const [job, setJob] =
    useState<GenerationJob | null>(null)

  const [starting, setStarting] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  async function generate() {
    try {
      setStarting(true)
      setError(null)

      const created =
        await createGenerationJob(
          caseId,
        )

      setJob(created)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo iniciar la generación",
      )
    } finally {
      setStarting(false)
    }
  }

  useEffect(() => {
    if (
      !job ||
      job.status === "completed" ||
      job.status === "failed"
    ) {
      return
    }

    const timer =
      globalThis.setInterval(
        async () => {
          try {
            const current =
              await getGenerationJob(
                job.id,
              )

            setJob(current)
          } catch (err) {
            setError(
              err instanceof Error
                ? err.message
                : "No se pudo actualizar la generación",
            )
          }
        },
        1500,
      )

    return () => {
      globalThis.clearInterval(timer)
    }
  }, [
    job?.id,
    job?.status,
  ])

  if (!job) {
    return (
      <section className="generation-panel">
        <div>
          <strong>
            Propuesta preparada
          </strong>

          <p>
            Genera la presentación utilizando
            los datos actuales de PrefWeb,
            las notas y las fotografías.
          </p>
        </div>

        <button
          className="generate-button"
          disabled={starting}
          onClick={() =>
            void generate()
          }
        >
          {starting
            ? "Iniciando..."
            : "Generar presentación"}
        </button>

        {error && (
          <div className="generation-error">
            {error}
          </div>
        )}
      </section>
    )
  }

  if (job.status === "failed") {
    return (
      <section className="generation-panel generation-failed">
        <div>
          <strong>
            No se pudo generar la presentación
          </strong>

          <p>
            La generación ha fallado.
            Puedes volver a intentarlo.
          </p>

          {job.error_message && (
            <details>
              <summary>
                Ver detalle
              </summary>

              <pre>
                {job.error_message}
              </pre>
            </details>
          )}
        </div>

        <button
          className="generate-button"
          onClick={() =>
            void generate()
          }
        >
          Volver a intentar
        </button>
      </section>
    )
  }

  if (job.status === "completed") {
    return (
      <section className="generation-panel generation-completed">
        <div>
          <strong>
            ✓ Presentación generada
          </strong>

          <p>
            {job.output_filename ??
              "La propuesta está lista para revisar."}
          </p>
        </div>

        <div className="generation-actions">
          {job.download_url && (
            <a
              className="review-button"
              href={job.download_url}
              target="_blank"
              rel="noreferrer"
            >
              Revisar presentación
            </a>
          )}

          <button
            className="send-button"
            disabled
            title="Se conectará posteriormente con Odoo"
          >
            Enviar al cliente
          </button>

          <button
            className="secondary-button"
            onClick={() =>
              void generate()
            }
          >
            Regenerar
          </button>
        </div>
      </section>
    )
  }

  const currentIndex =
    stepIndex(job.current_step)

  return (
    <section className="generation-progress-panel">
      <div className="generation-progress-header">
        <div>
          <strong>
            Generando propuesta...
          </strong>

          <p>
            Puedes seguir el progreso en tiempo real.
          </p>
        </div>

        <strong className="generation-percentage">
          {job.progress} %
        </strong>
      </div>

      <div className="generation-progress-bar">
        <div
          style={{
            width: `${job.progress}%`,
          }}
        />
      </div>

      <div className="generation-steps">
        {STEPS.map(
          (step, index) => {
            let symbol = "○"
            let className = "pending"

            if (
              index < currentIndex ||
              job.progress >= 100
            ) {
              symbol = "✓"
              className = "done"
            } else if (
              index === currentIndex
            ) {
              symbol = "●"
              className = "active"
            }

            return (
              <div
                key={step.key}
                className={
                  `generation-step ${className}`
                }
              >
                <span>
                  {symbol}
                </span>

                {step.label}
              </div>
            )
          },
        )}
      </div>

      {error && (
        <div className="generation-error">
          {error}
        </div>
      )}
    </section>
  )
}
