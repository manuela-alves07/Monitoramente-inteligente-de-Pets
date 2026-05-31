export async function buscarRelatorios() {
  const resposta = await fetch('/relatorios')
  return resposta.json()
}

export async function buscarRelatorio(nome) {
  const resposta = await fetch(`/relatorios/${nome}`)
  return resposta.json()
}

export async function analisarVideo(arquivo, idAnimal) {
  const form = new FormData()
  form.append('video', arquivo)
  if (idAnimal) form.append('id_animal', idAnimal)
  const resposta = await fetch('/analisar', { method: 'POST', body: form })
  if (!resposta.ok) throw new Error('Erro na análise')
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

export async function trocarMinhaSenha(login, senhaAtual, novaSenha) {
  const resposta = await fetch('/usuarios/me/senha', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, senha_atual: senhaAtual, nova_senha: novaSenha }),
  })
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}))
    throw new Error(erro.erro || 'Erro ao trocar senha')
  }
  return resposta.json()
}

export async function salvarObservacoes(idAnimal, observacoes) {
  const resposta = await fetch(`/animais/${idAnimal}/observacoes`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ observacoes }),
  })
  if (!resposta.ok) throw new Error('Erro ao salvar observações')
  return resposta.json()
}

export async function transferirBaia(idAnimal, idBaia) {
  const resposta = await fetch(`/animais/${idAnimal}/transferir`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_baia: idBaia }),
  })
  if (!resposta.ok) throw new Error('Erro ao transferir baia')
  return resposta.json()
}

export async function listarEventos(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/eventos`)
  if (!resposta.ok) throw new Error('Erro ao buscar eventos')
  return resposta.json()
}
