import type {
  ReferencePhoto,
  ReferenceSelection,
} from "./types"

import type {
  CaseWorkspace,
  GenerationJob,
  PrefWebProjectSummary,
  ProjectCase,
  WorkspaceWindow,
} from "./types"

async function request<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(url, options)

  if (!response.ok) {
    let message = `HTTP ${response.status}`

    try {
      const data = await response.json()

      if (data.detail) {
        message = data.detail
      }
    } catch {
      // Ignore invalid JSON errors.
    }

    throw new Error(message)
  }

  return response.json() as Promise<T>
}

export async function searchProjects(
  query: string,
  page = 1,
  pageSize = 20,
): Promise<PrefWebProjectSummary[]> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  })

  return request<PrefWebProjectSummary[]>(
    `/api/prefweb/projects?${params.toString()}`,
  )
}

export async function createCase(
  number: number,
  version: number,
): Promise<ProjectCase> {
  return request<ProjectCase>(
    "/api/cases",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prefweb_number: number,
        prefweb_version: version,
      }),
    },
  )
}

export async function getWorkspace(
  caseId: string,
): Promise<CaseWorkspace> {
  return request<CaseWorkspace>(
    `/api/cases/${caseId}/workspace`,
  )
}

export async function updateCase(
  caseId: string,
  data: {
    visit_notes: string | null
  },
): Promise<ProjectCase> {
  return request<ProjectCase>(
    `/api/cases/${caseId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    },
  )
}

export async function updateWindow(
  caseId: string,
  windowId: string,
  data: {
    problem_type: string | null
    commercial_notes: string | null
  },
): Promise<WorkspaceWindow> {
  return request<WorkspaceWindow>(
    `/api/cases/${caseId}/windows/${windowId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    },
  )
}

export async function uploadPhoto(
  caseId: string,
  windowId: string,
  file: File,
): Promise<void> {
  const form = new FormData()

  form.append("file", file)
  form.append("window_id", windowId)

  const response = await fetch(
    `/api/cases/${caseId}/photos`,
    {
      method: "POST",
      body: form,
    },
  )

  if (!response.ok) {
    let message =
      `Could not upload photo: HTTP ${response.status}`

    try {
      const data = await response.json()

      if (data.detail) {
        message = data.detail
      }
    } catch {
      // Ignore malformed JSON.
    }

    throw new Error(message)
  }
}

export async function deletePhoto(
  caseId: string,
  photoId: string,
): Promise<void> {
  const response = await fetch(
    `/api/cases/${caseId}/photos/${photoId}`,
    {
      method: "DELETE",
    },
  )

  if (!response.ok) {
    let message =
      `Could not delete photo: HTTP ${response.status}`

    try {
      const data = await response.json()

      if (data.detail) {
        message = data.detail
      }
    } catch {
      // Ignore malformed JSON.
    }

    throw new Error(message)
  }
}

export async function createGenerationJob(
  caseId: string,
): Promise<GenerationJob> {
  return request<GenerationJob>(
    `/api/cases/${caseId}/generation-jobs`,
    {
      method: "POST",
    },
  )
}

export async function getGenerationJob(
  jobId: string,
): Promise<GenerationJob> {
  return request<GenerationJob>(
    `/api/generation-jobs/${jobId}`,
  )
}

export async function getReferencePhotos(
  caseId: string,
): Promise<ReferenceSelection[]> {
  return request<ReferenceSelection[]>(
    `/api/cases/${caseId}/reference-photos`,
  )
}

export async function refreshReferencePhotos(
  caseId: string,
): Promise<ReferenceSelection[]> {
  return request<ReferenceSelection[]>(
    `/api/cases/${caseId}/reference-photos/refresh`,
    {
      method: "POST",
    },
  )
}

export async function confirmReferencePhotos(
  caseId: string,
): Promise<ReferenceSelection[]> {
  return request<ReferenceSelection[]>(
    `/api/cases/${caseId}/reference-photos/confirm`,
    {
      method: "POST",
    },
  )
}

export async function listReferencePhotoLibrary():
Promise<ReferencePhoto[]> {
  return request<ReferencePhoto[]>(
    "/api/reference-photos",
  )
}

export async function selectReferencePhoto(
  caseId: string,
  slot: number,
  referencePhotoId: string,
): Promise<ReferenceSelection> {
  return request<ReferenceSelection>(
    `/api/cases/${caseId}/reference-photos/${slot}`,
    {
      method: "PUT",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reference_photo_id:
          referencePhotoId,
      }),
    },
  )
}

export async function removeReferencePhoto(
  caseId: string,
  slot: number,
): Promise<void> {
  const response = await fetch(
    `/api/cases/${caseId}/reference-photos/${slot}`,
    {
      method: "DELETE",
    },
  )

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status}`,
    )
  }
}

export async function uploadReferencePhoto(
  caseId: string,
  slot: number,
  file: File,
): Promise<ReferenceSelection> {
  const form = new FormData()

  form.append(
    "file",
    file,
  )

  return request<ReferenceSelection>(
    `/api/cases/${caseId}/reference-photos/${slot}/upload`,
    {
      method: "POST",
      body: form,
    },
  )
}
