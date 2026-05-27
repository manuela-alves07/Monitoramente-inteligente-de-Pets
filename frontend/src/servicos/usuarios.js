export function usuarioAtual() {
  return {
    nome:  localStorage.getItem('vetvision-usuario') ?? '',
    role:  localStorage.getItem('vetvision-role')    ?? 'user',
    login: localStorage.getItem('vetvision-login')   ?? '',
  }
}

export function isAdmin() {
  return localStorage.getItem('vetvision-role') === 'admin'
}
