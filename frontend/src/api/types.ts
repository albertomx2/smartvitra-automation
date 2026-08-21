export interface PrefWebProjectSummary {
  row_id: string
  number: number
  alias_number: string
  version: number
  version_name: string

  customer_code: string | null
  customer_name: string

  request_date: string | null
  reference: string | null

  customer_nif: string | null
  customer_address: string | null
  customer_address2: string | null
  customer_postal_code: string | null
  customer_city: string | null
  customer_country: string | null

  is_active: boolean
  is_confirmed: boolean
  is_public: boolean

  subtotal: number
  tax: number
  final_price: number

  currency_symbol: string | null
  currency_name: string | null

  has_order: boolean
  has_factory_version: boolean
}

export interface WorkspacePhoto {
  id: string
  filename: string
  content_type: string
  description: string | null
  file_url: string
}

export interface WorkspaceWindow {
  id: string
  prefweb_item_id: string
  prefweb_id_pos: string | null

  position: number
  nomenclature: string | null
  reference: string | null
  description: string | null
  color: string | null
  dimensions: string | null
  quantity: number
  total_amount: number

  room: string | null

  problem_type: string | null
  commercial_notes: string | null

  prefweb_svg_url: string

  photos: WorkspacePhoto[]
}

export interface WorkspaceProject {
  number: number
  version: number

  alias_number: string
  version_name: string

  customer_name: string

  request_date: string | null
  reference: string | null

  customer_address: string | null
  customer_address2: string | null
  customer_postal_code: string | null
  customer_city: string | null
  customer_country: string | null

  subtotal: number
  tax: number
  final_price: number
  currency_symbol: string
}

export interface CaseWorkspace {
  id: string
  status: string
  visit_notes: string | null
  project: WorkspaceProject
  windows: WorkspaceWindow[]
}

export interface ProjectCase {
  id: string
  prefweb_number: number
  prefweb_version: number
  alias_number: string
  customer_name: string
  status: string
  visit_notes?: string | null
}

export type GenerationJobStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"

export interface GenerationArtifact {
  id: string
  kind:
    | "presentation"
    | "script"
    | "narration"
    | "video"
    | string

  filename: string
  content_type: string
  size_bytes: number
  download_url: string | null
}

export interface GenerationJob {
  id: string
  case_id: string

  status: GenerationJobStatus

  current_step: string | null
  progress: number

  input_snapshot: unknown | null

  output_filename: string | null
  download_url: string | null

  artifacts: GenerationArtifact[]

  error_message: string | null

  created_at: string
  started_at: string | null
  completed_at: string | null
}


export interface ReferencePhoto {
  id: string
  filename: string
  description: string | null

  problem_tags: string[]
  room_tags: string[]
  window_type_tags: string[]
  feature_tags: string[]

  file_url: string
}

export interface ReferenceSelection {
  slot: number
  status: string
  score: number | null

  photo: ReferencePhoto
}
