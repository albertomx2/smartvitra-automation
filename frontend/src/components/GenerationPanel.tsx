import {
  useEffect,
  useState,
} from "react"
import { downloadAuthenticatedFile } from "../api/client"

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

interface GenerationAttachment {
  id: string
  filename: string
  kind:
    | "pptx"
    | "pdf"
    | "script"
    | "audio"
    | "video"
    | "other"
  label: string
  downloadUrl: string
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
    key: "generating_script",
    label: "Generando guion personalizado",
  },
  {
    key: "generating_narration",
    label: "Preparando narración de prueba",
  },
  {
    key: "rendering_video",
    label: "Creando vídeo personalizado",
  },
  {
    key: "saving_outputs",
    label: "Guardando archivos",
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

function buildAttachments(
  job: GenerationJob,
): GenerationAttachment[] {
  if (
    job.artifacts &&
    job.artifacts.length > 0
  ) {
    return job.artifacts
      .filter(
        (artifact) =>
          artifact.download_url,
      )
      .map((artifact) => {
        let kind:
          GenerationAttachment["kind"] =
            "other"

        let label =
          "Archivo generado"

        if (
          artifact.kind ===
          "presentation"
        ) {
          kind = "pptx"
          label =
            "Presentación comercial"
        }

        if (
          artifact.kind ===
          "script"
        ) {
          kind = "script"
          label =
            "Guion comercial personalizado"
        }

        if (
          artifact.kind ===
          "narration"
        ) {
          kind = "audio"
          label =
            "Narración personalizada"
        }

        if (
          artifact.kind ===
          "video"
        ) {
          kind = "video"
          label =
            "Vídeo personalizado"
        }

        return {
          id: artifact.id,
          filename:
            artifact.filename,
          kind,
          label,
          downloadUrl:
            artifact.download_url!,
        }
      })
  }

  if (
    !job.output_filename ||
    !job.download_url
  ) {
    return []
  }

  return [
    {
      id: "presentation",
      filename:
        job.output_filename,
      kind: "pptx",
      label:
        "Presentación comercial",
      downloadUrl:
        job.download_url,
    },
  ]
}


function attachmentBadge(
  kind: GenerationAttachment["kind"],
): string {
  switch (kind) {
    case "pptx":
      return "PPT"
    case "pdf":
      return "PDF"
    case "script":
      return "JSON"
    case "audio":
      return "MP3"
    case "video":
      return "MP4"
    default:
      return "FILE"
  }
}

export default function GenerationPanel({
  caseId,
}: GenerationPanelProps) {
  const [job, setJob] =
    useState<GenerationJob | null>(null)

  const [starting, setStarting] =
    useState(false)

  const [reviewing, setReviewing] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  async function generate() {
    try {
      setStarting(true)
      setReviewing(false)
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
            : "Generar"}
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
            No se pudo generar la propuesta
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
    const attachments =
      buildAttachments(job)

    if (reviewing) {
      return (
        <section className="generation-review-panel">
          <div className="generation-review-header">
            <div>
              <strong>
                Revisar propuesta
              </strong>

              <p>
                Revisa los archivos generados
                antes de continuar.
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={() =>
                setReviewing(false)
              }
            >
              Cerrar revisión
            </button>
          </div>

          <div className="generation-attachments">
            <div className="generation-attachments-title">
              Archivos adjuntos
            </div>

            {attachments.length === 0 ? (
              <div className="generation-empty-attachments">
                No hay archivos disponibles.
              </div>
            ) : (
              attachments.map(
                (attachment) => (
                  <div
                    key={attachment.id}
                    className="generation-attachment"
                  >
                    <div className="generation-attachment-main">
                      <div className="generation-file-badge">
                        {attachmentBadge(
                          attachment.kind,
                        )}
                      </div>

                      <div className="generation-file-info">
                        <strong>
                          {attachment.filename}
                        </strong>

                        <span>
                          {attachment.label}
                        </span>
                      </div>
                    </div>

                    <a
                      className="attachment-download-button"
                      href="#"
                      onClick={async (event) => {
                        event.preventDefault()

                        await downloadAuthenticatedFile(
                          attachment.downloadUrl,
                          attachment.filename,
                        )
                      }}
                    >
                      Descargar
                    </a>
                  </div>
                ),
              )
            )}
          </div>

          <div className="generation-review-actions">
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

    return (
      <section className="generation-panel generation-completed">
        <div>
          <strong>
            ✓ Propuesta generada
          </strong>

          <p>
            La propuesta está lista para revisar.
          </p>
        </div>

        <div className="generation-actions">
          <button
            className="review-button"
            onClick={() =>
              setReviewing(true)
            }
          >
            Revisar propuesta
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
