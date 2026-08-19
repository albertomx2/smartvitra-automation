import {
  useEffect,
  useRef,
  useState,
} from "react"

import {
  createCase,
  deletePhoto,
  getWorkspace,
  searchProjects,
  updateCase,
  updateWindow,
  uploadPhoto,
} from "./api/client"

import type {
  CaseWorkspace,
  PrefWebProjectSummary,
  WorkspaceWindow,
} from "./api/types"

import GenerationPanel from "./components/GenerationPanel"
import ReferencePhotoSelector from "./components/ReferencePhotoSelector"

import "./App.css"
import AuthenticatedImage from "./components/AuthenticatedImage"

type SaveStatus =
  | "idle"
  | "saving"
  | "saved"
  | "error"

function formatMoney(
  amount: number,
): string {
  return new Intl.NumberFormat(
    "es-ES",
    {
      style: "currency",
      currency: "EUR",
    },
  ).format(amount)
}

function formatPrefWebDate(
  value: string | null,
): string {
  if (!value) {
    return ""
  }

  const match =
    /\/Date\((\d+)\)\//.exec(value)

  if (!match) {
    return value
  }

  return new Intl.DateTimeFormat(
    "es-ES",
  ).format(
    new Date(
      Number(match[1]),
    ),
  )
}

function SaveIndicator({
  status,
}: {
  status: SaveStatus
}) {
  if (status === "idle") {
    return null
  }

  return (
    <span
      className={`save-status save-status-${status}`}
    >
      {status === "saving" &&
        "Guardando…"}

      {status === "saved" &&
        "Guardado ✓"}

      {status === "error" &&
        "Error al guardar"}
    </span>
  )
}

function App() {
  const [query, setQuery] =
    useState("")

  const [results, setResults] =
    useState<
      PrefWebProjectSummary[]
    >([])

  const [workspace, setWorkspace] =
    useState<CaseWorkspace | null>(
      null,
    )

  const [loading, setLoading] =
    useState(false)

  const [openingProject, setOpeningProject] =
    useState<string | null>(
      null,
    )

  const [error, setError] =
    useState<string | null>(
      null,
    )

  useEffect(() => {
    const timeout =
      globalThis.setTimeout(
        async () => {
          try {
            setLoading(true)
            setError(null)

            const projects =
              await searchProjects(
                query.trim(),
                1,
                20,
              )

            setResults(
              projects,
            )
          } catch (err) {
            setError(
              err instanceof Error
                ? err.message
                : "Error cargando presupuestos",
            )
          } finally {
            setLoading(false)
          }
        },
        300,
      )

    return () => {
      globalThis.clearTimeout(
        timeout,
      )
    }
  }, [query])

  async function openProject(
    project: PrefWebProjectSummary,
  ) {
    const key =
      `${project.number}-${project.version}`

    try {
      setOpeningProject(
        key,
      )

      setError(null)

      const projectCase =
        await createCase(
          project.number,
          project.version,
        )

      const loadedWorkspace =
        await getWorkspace(
          projectCase.id,
        )

      setWorkspace(
        loadedWorkspace,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error abriendo presupuesto",
      )
    } finally {
      setOpeningProject(
        null,
      )
    }
  }

  async function refreshWorkspace() {
    if (!workspace) {
      return
    }

    const updated =
      await getWorkspace(
        workspace.id,
      )

    setWorkspace(
      updated,
    )
  }

  if (workspace) {
    return (
      <main className="app">
        <header className="topbar">
          <div>
            <div className="brand">
              SmartVitra
            </div>

            <div className="subtitle">
              Preparación de propuesta comercial
            </div>
          </div>

          <button
            className="secondary-button"
            onClick={() => {
              setWorkspace(null)
              setQuery("")
              setError(null)
            }}
          >
            Cambiar presupuesto
          </button>
        </header>

        <section className="project-header">
          <div>
            <div className="eyebrow">
              Presupuesto{" "}
              {
                workspace.project
                  .alias_number
              }
              {" · "}
              {
                workspace.project
                  .version_name
              }
            </div>

            <h1>
              {
                workspace.project
                  .customer_name
              }
            </h1>

            <div className="project-meta">
              {workspace.project
                .request_date && (
                <>
                  {
                    workspace
                      .project
                      .request_date
                  }
                  {" · "}
                </>
              )}

              {
                workspace.windows
                  .length
              }{" "}
              ventanas

              {workspace.project
                .reference && (
                <>
                  {" · Ref. "}
                  {
                    workspace
                      .project
                      .reference
                  }
                </>
              )}
            </div>
          </div>

          <div className="project-price">
            {formatMoney(
              workspace.project
                .final_price,
            )}
          </div>
        </section>

        <VisitNotes
          caseId={workspace.id}
          initialValue={
            workspace.visit_notes
          }
        />

        <section className="windows">
          {workspace.windows.map(
            (window) => (
              <WindowCard
                key={window.id}
                caseId={
                  workspace.id
                }
                window={window}
                onChanged={
                  refreshWorkspace
                }
              />
            ),
          )}
        </section>

        <ReferencePhotoSelector
          caseId={workspace.id}
        />

        <GenerationPanel
          caseId={workspace.id}
        />
      </main>
    )
  }

  return (
    <main className="app">
      <header className="welcome">
        <div className="brand">
          SmartVitra
        </div>

        <h1>
          Preparar una propuesta
        </h1>

        <p>
          Selecciona un presupuesto de PrefWeb.
        </p>
      </header>

      <section className="search-panel">
        <div className="search-row">
          <input
            value={query}
            autoFocus
            placeholder="Buscar cliente, referencia o presupuesto"
            onChange={(event) =>
              setQuery(
                event.target.value,
              )
            }
          />
        </div>

        <div className="results-heading">
          <div>
            <strong>
              {query.trim()
                ? "Resultados"
                : "Presupuestos recientes"}
            </strong>

            {!loading && (
              <span className="result-count">
                {
                  results.length
                }{" "}
                resultados
              </span>
            )}
          </div>

          {loading && (
            <span>
              Actualizando…
            </span>
          )}
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {!loading &&
          results.length === 0 &&
          !error && (
            <div className="empty-results">
              No se encontraron presupuestos.
            </div>
          )}

        <div className="results">
          {results.map(
            (project) => {
              const key =
                `${project.number}-${project.version}`

              const location =
                [
                  project.customer_address,
                  project.customer_city,
                ]
                  .filter(Boolean)
                  .join(" · ")

              return (
                <button
                  className="project-result"
                  key={key}
                  disabled={
                    openingProject !==
                      null
                  }
                  onClick={() =>
                    void openProject(
                      project,
                    )
                  }
                >
                  <div className="project-result-main">
                    <div className="project-result-title-row">
                      <strong>
                        {
                          project.customer_name
                        }
                      </strong>

                      {project.is_active && (
                        <span className="status-pill active">
                          Activo
                        </span>
                      )}

                      {project.has_order && (
                        <span className="status-pill">
                          Pedido
                        </span>
                      )}
                    </div>

                    <span>
                      {
                        project.alias_number
                      }
                      {" · "}
                      {
                        project.version_name
                      }

                      {project.request_date && (
                        <>
                          {" · "}
                          {formatPrefWebDate(
                            project.request_date,
                          )}
                        </>
                      )}
                    </span>

                    {(project.reference ||
                      location) && (
                      <span className="result-detail">
                        {project.reference &&
                          `Ref. ${project.reference}`}

                        {project.reference &&
                          location &&
                          " · "}

                        {location}
                      </span>
                    )}
                  </div>

                  <div className="project-result-price">
                    <strong>
                      {formatMoney(
                        project.final_price,
                      )}
                    </strong>

                    <span>
                      {openingProject ===
                      key
                        ? "Abriendo…"
                        : "Abrir →"}
                    </span>
                  </div>
                </button>
              )
            },
          )}
        </div>
      </section>
    </main>
  )
}

function VisitNotes({
  caseId,
  initialValue,
}: {
  caseId: string
  initialValue: string | null
}) {
  const [notes, setNotes] =
    useState(
      initialValue ?? "",
    )

  const [status, setStatus] =
    useState<SaveStatus>(
      "idle",
    )

  const lastSaved =
    useRef(
      initialValue ?? "",
    )

  useEffect(() => {
    setNotes(
      initialValue ?? "",
    )

    lastSaved.current =
      initialValue ?? ""
  }, [initialValue])

  useEffect(() => {
    if (
      notes ===
      lastSaved.current
    ) {
      return
    }

    const timeout =
      globalThis.setTimeout(
        async () => {
          setStatus(
            "saving",
          )

          try {
            await updateCase(
              caseId,
              {
                visit_notes:
                  notes.trim()
                    ? notes
                    : null,
              },
            )

            lastSaved.current =
              notes

            setStatus(
              "saved",
            )
          } catch {
            setStatus(
              "error",
            )
          }
        },
        650,
      )

    return () => {
      globalThis.clearTimeout(
        timeout,
      )
    }
  }, [
    caseId,
    notes,
  ])

  return (
    <section className="visit-notes-card">
      <div className="section-title-row">
        <div>
          <div className="eyebrow">
            Visita comercial
          </div>

          <h2>
            Notas generales
          </h2>
        </div>

        <SaveIndicator
          status={status}
        />
      </div>

      <textarea
        value={notes}
        placeholder="Observaciones generales de la visita, prioridades del cliente, contexto de la vivienda..."
        onChange={(event) =>
          setNotes(
            event.target.value,
          )
        }
      />
    </section>
  )
}

interface WindowCardProps {
  caseId: string
  window: WorkspaceWindow
  onChanged: () => Promise<void>
}

function WindowCard({
  caseId,
  window,
  onChanged,
}: WindowCardProps) {
  const [problemType, setProblemType] =
    useState(
      window.problem_type ??
        "",
    )

  const [notes, setNotes] =
    useState(
      window.commercial_notes ??
        "",
    )

  const [saveStatus, setSaveStatus] =
    useState<SaveStatus>(
      "idle",
    )

  const [uploading, setUploading] =
    useState(false)

  const [deletingPhoto, setDeletingPhoto] =
    useState<string | null>(
      null,
    )

  const [photoError, setPhotoError] =
    useState<string | null>(
      null,
    )

  const lastSaved =
    useRef({
      problemType:
        window.problem_type ??
        "",
      notes:
        window.commercial_notes ??
        "",
    })

  useEffect(() => {
    const nextProblem =
      window.problem_type ??
      ""

    const nextNotes =
      window.commercial_notes ??
      ""

    setProblemType(
      nextProblem,
    )

    setNotes(
      nextNotes,
    )

    lastSaved.current = {
      problemType:
        nextProblem,
      notes:
        nextNotes,
    }
  }, [
    window.problem_type,
    window.commercial_notes,
  ])

  useEffect(() => {
    if (
      problemType ===
        lastSaved.current
          .problemType &&
      notes ===
        lastSaved.current.notes
    ) {
      return
    }

    const timeout =
      globalThis.setTimeout(
        async () => {
          setSaveStatus(
            "saving",
          )

          try {
            await updateWindow(
              caseId,
              window.id,
              {
                problem_type:
                  problemType ||
                  null,
                commercial_notes:
                  notes.trim()
                    ? notes
                    : null,
              },
            )

            lastSaved.current = {
              problemType,
              notes,
            }

            setSaveStatus(
              "saved",
            )
          } catch {
            setSaveStatus(
              "error",
            )
          }
        },
        650,
      )

    return () => {
      globalThis.clearTimeout(
        timeout,
      )
    }
  }, [
    caseId,
    window.id,
    problemType,
    notes,
  ])

  async function addPhotos(
    files: FileList | File[],
  ) {
    const selected =
      Array.from(files)

    if (
      selected.length === 0
    ) {
      return
    }

    setUploading(true)
    setPhotoError(null)

    try {
      for (const file of selected) {
        await uploadPhoto(
          caseId,
          window.id,
          file,
        )
      }

      await onChanged()
    } catch (err) {
      setPhotoError(
        err instanceof Error
          ? err.message
          : "No se pudieron subir las fotos",
      )
    } finally {
      setUploading(false)
    }
  }

  async function removePhoto(
    photoId: string,
  ) {
    setDeletingPhoto(
      photoId,
    )

    setPhotoError(null)

    try {
      await deletePhoto(
        caseId,
        photoId,
      )

      await onChanged()
    } catch (err) {
      setPhotoError(
        err instanceof Error
          ? err.message
          : "No se pudo eliminar la foto",
      )
    } finally {
      setDeletingPhoto(
        null,
      )
    }
  }

  return (
    <article className="window-card">
      <div className="window-heading">
        <div>
          <div className="eyebrow">
            {window.nomenclature ??
              `Ventana ${window.position}`}
          </div>

          <h2>
            {window.room ||
              `Ventana ${window.position}`}
          </h2>

          <p>
            {window.description}
          </p>
        </div>

        <div className="window-price">
          {formatMoney(
            window.total_amount,
          )}
        </div>
      </div>

      <div className="window-grid">
        <div className="window-preview">
          <AuthenticatedImage
            src={
              window.prefweb_svg_url
            }
            alt={`Diseño ${window.room ?? ""}`}
          />

          <div className="technical-data">
            {window.dimensions && (
              <span>
                {
                  window.dimensions
                }
              </span>
            )}

            {window.color && (
              <span>
                {window.color}
              </span>
            )}

            {window.reference && (
              <span>
                Ref.{" "}
                {
                  window.reference
                }
              </span>
            )}
          </div>
        </div>

        <div className="commercial-data">
          <div className="commercial-header">
            <strong>
              Información de visita
            </strong>

            <SaveIndicator
              status={
                saveStatus
              }
            />
          </div>

          <label>
            Problema principal

            <select
              value={
                problemType
              }
              onChange={(
                event,
              ) =>
                setProblemType(
                  event.target
                    .value,
                )
              }
            >
              <option value="">
                Sin especificar
              </option>

              <option value="noise">
                Ruido
              </option>

              <option value="thermal">
                Aislamiento térmico
              </option>

              <option value="air">
                Corrientes de aire
              </option>

              <option value="security">
                Seguridad
              </option>

              <option value="aesthetic">
                Estética
              </option>

              <option value="other">
                Otro
              </option>
            </select>
          </label>

          <label>
            Notas del comercial

            <textarea
              value={notes}
              placeholder="Ej. mucho ruido de tráfico por la noche, condensación, entra frío..."
              onChange={(
                event,
              ) =>
                setNotes(
                  event.target
                    .value,
                )
              }
            />
          </label>
        </div>
      </div>

      <div className="photos-section">
        <div className="photos-header">
          <div>
            <strong>
              Fotos de la estancia
            </strong>

            <span className="photos-count">
              {
                window.photos
                  .length
              }{" "}
              fotos
            </span>
          </div>

          <div className="photo-actions">
            <label className="upload-button camera-button">
              📷 Hacer foto

              <input
                type="file"
                accept="image/*"
                capture="environment"
                disabled={
                  uploading
                }
                onChange={(
                  event,
                ) => {
                  const files =
                    event.target
                      .files

                  if (files) {
                    void addPhotos(
                      files,
                    )
                  }

                  event.target.value =
                    ""
                }}
              />
            </label>

            <label className="upload-button">
              {uploading
                ? "Subiendo…"
                : "Elegir archivos"}

              <input
                type="file"
                accept="image/*"
                multiple
                disabled={
                  uploading
                }
                onChange={(
                  event,
                ) => {
                  const files =
                    event.target
                      .files

                  if (files) {
                    void addPhotos(
                      files,
                    )
                  }

                  event.target.value =
                    ""
                }}
              />
            </label>
          </div>
        </div>

        {photoError && (
          <div className="photo-error">
            {photoError}
          </div>
        )}

        {uploading && (
          <div className="upload-progress">
            Subiendo fotografías…
          </div>
        )}

        {window.photos.length ===
        0 ? (
          <div className="empty-photos">
            Todavía no hay fotos.
            Puedes hacer una foto directamente o elegir varias desde el dispositivo.
          </div>
        ) : (
          <div className="photos-grid">
            {window.photos.map(
              (photo) => (
                <div
                  className="photo-card"
                  key={
                    photo.id
                  }
                >
                  <AuthenticatedImage
                    src={
                      photo.file_url
                    }
                    alt={
                      photo.description ??
                      photo.filename
                    }
                  />

                  <button
                    type="button"
                    className="photo-delete"
                    aria-label="Eliminar foto"
                    title="Eliminar foto"
                    disabled={
                      deletingPhoto ===
                      photo.id
                    }
                    onClick={() =>
                      void removePhoto(
                        photo.id,
                      )
                    }
                  >
                    {deletingPhoto ===
                    photo.id
                      ? "…"
                      : "×"}
                  </button>
                </div>
              ),
            )}
          </div>
        )}
      </div>
    </article>
  )
}

export default App
