const CHAVE = 'vetvision-usuario'

export function salvarUsuarioLogado(usuario) {
  localStorage.setItem(CHAVE, JSON.stringify(usuario))
}

export function usuarioLogado() {
  const bruto = localStorage.getItem(CHAVE)
  if (!bruto) return null
  try {
    const valor = JSON.parse(bruto)
    if (valor && typeof valor === 'object' && valor.email) return valor
    return null
  } catch {
    return null
  }
}

export function idClinicaLogada() {
  return usuarioLogado()?.id_clinica ?? null
}

export function sair() {
  localStorage.removeItem(CHAVE)
}

export function inicialAvatar() {
  const u = usuarioLogado()
  const fonte = u?.nome || u?.email || 'U'
  return fonte.trim()[0]?.toUpperCase() || 'U'
}
