export async function analisarVideo(arquivo, idAnimal) {
  const form = new FormData()
  form.append('video', arquivo)
  if (idAnimal) form.append('id_animal', idAnimal)
  const resposta = await fetch('/analisar', { method: 'POST', body: form })
  if (!resposta.ok) {
    const body = await resposta.json().catch(() => ({}))
    throw new Error(body.erro || 'Erro na análise')
  }
  return resposta.json()
}

export async function listarBaias() {
  const resposta = await fetch('/baias')
  if (!resposta.ok) throw new Error('Erro ao buscar baias')
  return resposta.json()
}

export async function criarBaia() {
  const resposta = await fetch('/baias', { method: 'POST' })
  if (!resposta.ok) throw new Error('Erro ao criar baia')
  return resposta.json()
}

export async function excluirBaia(idBaia) {
  const resposta = await fetch(`/baias/${idBaia}`, { method: 'DELETE' })
  if (!resposta.ok) throw new Error('Erro ao remover baia')
  return resposta.json()
}

export async function listarAnimais() {
  const resposta = await fetch('/animais')
  if (!resposta.ok) throw new Error('Erro ao buscar animais')
  return resposta.json()
}

export async function cadastrarAnimal(dados) {
  const resposta = await fetch('/animais', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  })
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}))
    throw new Error(erro.erro || 'Erro ao cadastrar animal')
  }
  return resposta.json()
}

export async function buscarAnimal(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}`)
  if (!resposta.ok) throw new Error('Erro ao buscar animal')
  return resposta.json()
}

export async function atualizarAnimal(idAnimal, dados) {
  const resposta = await fetch(`/animais/${idAnimal}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  })
  if (!resposta.ok) throw new Error('Erro ao atualizar animal')
  return resposta.json()
}

export async function darBaixa(idAnimal, dadosAlta = {}) {
  const resposta = await fetch(`/animais/${idAnimal}/baixa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dadosAlta),
  })
  if (!resposta.ok) throw new Error('Erro ao dar baixa')
  return resposta.json()
}

export async function loginUsuario(login, senha) {
  const resposta = await fetch('/usuarios/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, senha }),
  })
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}))
    throw new Error(erro.erro || 'Usuário ou senha incorretos')
  }
  return resposta.json()
}

export async function listarUsuarios() {
  const resposta = await fetch('/usuarios')
  if (!resposta.ok) throw new Error('Erro ao buscar usuários')
  return resposta.json()
}

export async function cadastrarUsuario(dados) {
  const resposta = await fetch('/usuarios', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  })
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}))
    throw new Error(erro.erro || 'Erro ao cadastrar usuário')
  }
  return resposta.json()
}

export async function removerUsuario(idUsuario) {
  const resposta = await fetch(`/usuarios/${idUsuario}`, { method: 'DELETE' })
  if (!resposta.ok) throw new Error('Erro ao remover usuário')
  return resposta.json()
}

export async function atualizarSenha(idUsuario, senha) {
  const resposta = await fetch(`/usuarios/${idUsuario}/senha`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ senha }),
  })
  if (!resposta.ok) throw new Error('Erro ao atualizar senha')
  return resposta.json()
}

export async function listarEventos(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/eventos`)
  if (!resposta.ok) throw new Error('Erro ao buscar eventos')
  return resposta.json()
}

export async function buscarRelatorioAnimal(idAnimal, { data, id } = {}) {
  let url = `/animais/${idAnimal}/relatorio`
  if (id)        url += `?id=${id}`
  else if (data) url += `?data=${encodeURIComponent(data)}`
  const resposta = await fetch(url)
  if (resposta.status === 404) return null
  if (!resposta.ok) throw new Error('Erro ao buscar relatório do animal')
  return resposta.json()
}

export async function listarRelatoriosAnimal(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/relatorios`)
  if (!resposta.ok) throw new Error('Erro ao listar relatórios')
  return resposta.json()
}
