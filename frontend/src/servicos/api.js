export async function buscarRelatorios() {
  const resposta = await fetch('/relatorios')
  return resposta.json()
}

export async function buscarRelatorio(nome) {
  const resposta = await fetch(`/relatorios/${nome}`)
  return resposta.json()
}

export async function analisarVideo(arquivo) {
  const form = new FormData()
  form.append('video', arquivo)
  const resposta = await fetch('/analisar', { method: 'POST', body: form })
  if (!resposta.ok) throw new Error('Erro na análise')
  return resposta.json()
}
