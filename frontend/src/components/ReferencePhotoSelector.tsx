import {
  useEffect,
  useState,
} from "react"

import {
  confirmReferencePhotos,
  getReferencePhotos,
  listReferencePhotoLibrary,
  refreshReferencePhotos,
  removeReferencePhoto,
  selectReferencePhoto,
  uploadReferencePhoto,
} from "../api/client"

import type {
  ReferencePhoto,
  ReferenceSelection,
} from "../api/types"

interface Props {
  caseId: string
}

function ReferencePhotoSelector({
  caseId,
}: Props) {
  const [selections, setSelections] =
    useState<ReferenceSelection[]>([])

  const [library, setLibrary] =
    useState<ReferencePhoto[]>([])

  const [loading, setLoading] =
    useState(true)

  const [changingSlot, setChangingSlot] =
    useState<number | null>(null)

  const [error, setError] =
    useState<string | null>(null)

  async function load() {
    try {
      setLoading(true)
      setError(null)

      const [
        selected,
        available,
      ] = await Promise.all([
        getReferencePhotos(caseId),
        listReferencePhotoLibrary(),
      ])

      setSelections(selected)
      setLibrary(available)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudieron cargar los trabajos.",
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [caseId])

  async function refresh() {
    try {
      setLoading(true)

      const result =
        await refreshReferencePhotos(
          caseId,
        )

      setSelections(result)
      setChangingSlot(null)
    } finally {
      setLoading(false)
    }
  }

  async function confirm() {
    try {
      const result =
        await confirmReferencePhotos(
          caseId,
        )

      setSelections(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo confirmar.",
      )
    }
  }

  async function choose(
    slot: number,
    photoId: string,
  ) {
    const selection =
      await selectReferencePhoto(
        caseId,
        slot,
        photoId,
      )

    setSelections(
      (current) => [
        ...current.filter(
          (item) =>
            item.slot !== slot,
        ),
        selection,
      ].sort(
        (a, b) =>
          a.slot - b.slot,
      ),
    )

    setChangingSlot(null)
  }

  async function remove(
    slot: number,
  ) {
    await removeReferencePhoto(
      caseId,
      slot,
    )

    setSelections(
      (current) =>
        current.filter(
          (item) =>
            item.slot !== slot,
        ),
    )
  }

  async function upload(
    slot: number,
    file: File,
  ) {
    const selection =
      await uploadReferencePhoto(
        caseId,
        slot,
        file,
      )

    setSelections(
      (current) => [
        ...current.filter(
          (item) =>
            item.slot !== slot,
        ),
        selection,
      ].sort(
        (a, b) =>
          a.slot - b.slot,
      ),
    )

    setChangingSlot(null)

    setLibrary(
      await listReferencePhotoLibrary(),
    )
  }

  const allConfirmed =
    selections.length > 0
    && selections.every(
      (item) =>
        item.status === "confirmed",
    )

  if (loading) {
    return (
      <section className="reference-panel">
        <strong>
          Buscando trabajos similares...
        </strong>
      </section>
    )
  }

  return (
    <section className="reference-panel">
      <div className="reference-heading">
        <div>
          <div className="eyebrow">
            Trabajos SmartVitra
          </div>

          <h2>
            Trabajos relacionados
          </h2>

          <p>
            Hemos seleccionado trabajos
            similares según las necesidades
            de este proyecto.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() =>
            void refresh()
          }
        >
          Actualizar sugerencias
        </button>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      <div className="reference-grid">
        {[1, 2, 3].map(
          (slot) => {
            const selection =
              selections.find(
                (item) =>
                  item.slot === slot,
              )

            return (
              <article
                className="reference-card"
                key={slot}
              >
                <div className="reference-slot">
                  Trabajo {slot}
                </div>

                {selection ? (
                  <>
                    <img
                      src={
                        selection
                          .photo
                          .file_url
                      }
                      alt={
                        selection
                          .photo
                          .description
                        ?? selection
                          .photo
                          .filename
                      }
                    />

                    <div className="reference-description">
                      {
                        selection
                          .photo
                          .description
                        ?? "Trabajo SmartVitra"
                      }
                    </div>

                    <div className="reference-status">
                      {
                        selection.status
                        === "confirmed"
                          ? "✓ Confirmado"
                          : "Sugerido"
                      }
                    </div>
                  </>
                ) : (
                  <div className="reference-empty">
                    Sin fotografía seleccionada
                  </div>
                )}

                <div className="reference-actions">
                  <button
                    className="secondary-button"
                    onClick={() =>
                      setChangingSlot(
                        changingSlot
                        === slot
                          ? null
                          : slot,
                      )
                    }
                  >
                    Cambiar
                  </button>

                  {selection && (
                    <button
                      className="text-button danger"
                      onClick={() =>
                        void remove(
                          slot,
                        )
                      }
                    >
                      Quitar
                    </button>
                  )}

                  <label className="upload-button">
                    Subir otra

                    <input
                      type="file"
                      accept="image/*"
                      onChange={(
                        event,
                      ) => {
                        const file =
                          event.target
                            .files?.[0]

                        if (file) {
                          void upload(
                            slot,
                            file,
                          )
                        }

                        event.target.value =
                          ""
                      }}
                    />
                  </label>
                </div>

                {changingSlot
                  === slot && (
                  <div className="reference-library">
                    <strong>
                      Biblioteca
                    </strong>

                    <div className="reference-library-grid">
                      {library.map(
                        (photo) => (
                          <button
                            key={
                              photo.id
                            }
                            className="library-photo"
                            onClick={() =>
                              void choose(
                                slot,
                                photo.id,
                              )
                            }
                          >
                            <img
                              src={
                                photo.file_url
                              }
                              alt={
                                photo.description
                                ?? photo.filename
                              }
                            />
                          </button>
                        ),
                      )}
                    </div>
                  </div>
                )}
              </article>
            )
          },
        )}
      </div>

      <div className="reference-confirm">
        <div>
          <strong>
            {allConfirmed
              ? "✓ Selección confirmada"
              : "¿Usamos estos trabajos?"}
          </strong>

          <p>
            Puedes sustituir cualquiera
            antes de generar la propuesta.
          </p>
        </div>

        {!allConfirmed && (
          <button
            className="save-button"
            disabled={
              selections.length === 0
            }
            onClick={() =>
              void confirm()
            }
          >
            Usar selección
          </button>
        )}
      </div>
    </section>
  )
}

export default ReferencePhotoSelector
