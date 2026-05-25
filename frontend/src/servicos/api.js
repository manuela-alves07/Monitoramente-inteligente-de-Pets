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

export async function darBaixa(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/baixa`, { method: 'POST' })
  if (!resposta.ok) throw new Error('Erro ao dar baixa')
  return resposta.json()
}

export async function listarEventos(idAnimal) {
  const resposta = await fetch(`/animais/${idAnimal}/eventos`)
  if (!resposta.ok) throw new Error('Erro ao buscar eventos')
  return resposta.json()
}
