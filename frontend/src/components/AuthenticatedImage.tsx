import {
  useEffect,
  useState,
  type ImgHTMLAttributes,
} from "react"

import {
  createAuthenticatedObjectUrl,
} from "../api/client"

type Props =
  Omit<
    ImgHTMLAttributes<HTMLImageElement>,
    "src"
  > & {
    src: string
  }

function AuthenticatedImage({
  src,
  alt,
  ...props
}: Props) {
  const [objectUrl, setObjectUrl] =
    useState<string | null>(null)

  const [failed, setFailed] =
    useState(false)

  useEffect(() => {
    let active = true
    let createdUrl:
      | string
      | null = null

    setObjectUrl(null)
    setFailed(false)

    createAuthenticatedObjectUrl(
      src,
    )
      .then((url) => {
        createdUrl = url

        if (active) {
          setObjectUrl(url)
        } else {
          URL.revokeObjectURL(url)
        }
      })
      .catch(() => {
        if (active) {
          setFailed(true)
        }
      })

    return () => {
      active = false

      if (createdUrl) {
        URL.revokeObjectURL(
          createdUrl,
        )
      }
    }
  }, [src])

  if (failed) {
    return (
      <span>
        {alt ?? "Imagen no disponible"}
      </span>
    )
  }

  if (!objectUrl) {
    return (
      <span>
        Cargando imagen…
      </span>
    )
  }

  return (
    <img
      src={objectUrl}
      alt={alt}
      {...props}
    />
  )
}

export default AuthenticatedImage
