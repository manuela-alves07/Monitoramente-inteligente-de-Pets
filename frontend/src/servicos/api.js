import { idClinicaLogada } from './sessao'

async function pegarJson(resposta, mensagemPadrao) {
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}))
    throw new Error(erro.erro || mensagemPadrao)
  }
  return resposta.json()
}

function headersClinica(extra = {}) {
  const id = idClinicaLogada()
  if (!id) return extra
  return { ...extra, 'X-Id-Clinica': String(id) }
}

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
  const resposta = await fetch('/analisar', {
    method: 'POST',
    headers: headersClinica(),
    body: form,
  })
  return pegarJson(resposta, 'Erro na análise do vídeo')
}

export async function fazerLogin(email, senha) {
  const resposta = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha }),
  })
  return pegarJson(resposta, 'Usuário ou senha inválidos')
}

export async function listarBaias() {
  const resposta = await fetch('/baias', { headers: headersClinica() })
  return pegarJson(resposta, 'Erro ao buscar baias')
}

export async function cadastrarAnimal(dados) {
  const resposta = await fetch('/animais', {
    method: 'POST',
    headers: headersClinica({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(dados),
  })
  return pegarJson(resposta, 'Erro ao cadastrar animal')
}

export async function darBaixa(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/baixa`, {
    method: 'POST',
    headers: headersClinica(),
  })
  return pegarJson(resposta, 'Erro ao dar baixa')
}

export async function listarEventos(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/eventos`, {
    headers: headersClinica(),
  })
  return pegarJson(resposta, 'Erro ao buscar eventos')
}
